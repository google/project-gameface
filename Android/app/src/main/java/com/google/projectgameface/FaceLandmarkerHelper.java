/*
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.google.projectgameface;

import android.annotation.SuppressLint;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Matrix;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Message;
import android.os.Process;
import android.os.SystemClock;
import android.util.Log;
import android.view.Surface;
import androidx.annotation.NonNull;
import androidx.camera.core.ImageProxy;
import com.google.mediapipe.framework.image.BitmapImageBuilder;
import com.google.mediapipe.framework.image.MPImage;
import com.google.mediapipe.tasks.core.BaseOptions;
import com.google.mediapipe.tasks.core.Delegate;
import com.google.mediapipe.tasks.vision.core.RunningMode;
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarker;
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarkerResult;

/** The helper of camera feed. */
class FaceLandmarkerHelper extends HandlerThread {

    public static final String TAG = "FaceLandmarkerHelper";

    // number of allowed multiple detection works at the sametime.
    private static final int N_WORKS_LIMIT = 1;

    // Indicates if have new face landmarks detected.

    // Internal resolution for MediaPipe
    // this highly effect the performance.
    private static final float MP_WIDTH = 213.0f;
    private static final float MP_HEIGHT = 160.0f;

    private static final int TOTAL_BLENDSHAPES = 52;
    private static final int FOREHEAD_INDEX = 8;

    public volatile boolean isRunning = false;

    // Configs for FaceLandmarks model.
    private static final float MIN_FACE_DETECTION_CONFIDENCE = 0.5f;
    private static final float MIN_FACE_TRACKING_CONFIDENCE = 0.5f;
    private static final float MIN_FACE_PRESENCE_CONFIDENCE = 0.5f;
    private static final int MAX_NUM_FACES = 1;
    private static final RunningMode RUNNING_MODE = RunningMode.LIVE_STREAM;

    private Context context;

    private FaceLandmarker faceLandmarker = null;

    public int frameWidth = 0;
    public int frameHeight = 0;

    float currHeadX = 0.f;
    float currHeadY = 0.f;

    public long mediapipeTimeMs = 0;
    public long preprocessTimeMs = 0;


    // tracking how many works in process.
    private int currentInWorks = 0;

    private Handler handler;
    public int mpInputWidth;
    public int mpInputHeight;
    private float[] currBlendshapes;

    /** How many milliseconds passed after previous image. */
    public long gapTimeMs = 1;

    public long prevCallbackTimeMs = 0;

    public long timeSinceLastMeasurement = 0;
    private long lastMeasurementTsMs;

    FaceLandmarker.FaceLandmarkerOptions options;
    public boolean isFaceVisible;
    public int frontCameraOrientation = 270;



    // Frame rotation state for MediaPipe graph.
    private int currentRotationState = Surface.ROTATION_0;

    public FaceLandmarkerHelper() {
        super(TAG);
    }


    public void setFrontCameraOrientation(int orientation) {
        frontCameraOrientation = orientation;
    }



    /**
     * Sets internal frame rotation state for the MediaPipe graph.
     *
     * @param rotationValue Current rotation of the device screen, the value should be {@link
     *     Surface#ROTATION_0}, {@link Surface#ROTATION_90}, {@link Surface#ROTATION_180} or {@link
     *     Surface#ROTATION_180}.
     */
    public void setRotation(int rotationValue) {
        currentRotationState = rotationValue;
        Log.i(TAG, "setRotation: " + rotationValue);
    }

    @SuppressLint("HandlerLeak")
    @Override
    protected void onLooperPrepared() {
        handler =
            new Handler() {
                @Override
                public void handleMessage(@NonNull Message msg) {
                    // Function for handle message from main thread.
                    detectLiveStream((ImageProxy) msg.obj);

                }
            };
    }

    public Handler getHandler() {
        return handler;
    }

    /**
     * Create and configure the {@link FaceLandmarker}.
     *
     * @param context context for assets file loading.
     */
    public void init(Context context) {

        Log.i(TAG, "init : " + Thread.currentThread());
        Process.setThreadPriority(Process.THREAD_PRIORITY_URGENT_DISPLAY);
        isRunning = true;

        currBlendshapes = new float[TOTAL_BLENDSHAPES];

        this.context = context;

        // Set general FaceLandmarker options.
        Log.i(TAG, "Init MediaPipe");
        BaseOptions.Builder baseOptionBuilder = BaseOptions.builder();
        baseOptionBuilder.setDelegate(Delegate.GPU);
        baseOptionBuilder.setModelAssetPath("face_landmarker.task");

        try {
            BaseOptions baseOptions = baseOptionBuilder.build();
            // Create an option builder with base options and specific
            // options only use for Face Landmarker.
            FaceLandmarker.FaceLandmarkerOptions.Builder optionsBuilder =
                FaceLandmarker.FaceLandmarkerOptions.builder()
                    .setBaseOptions(baseOptions)
                    .setMinFaceDetectionConfidence(MIN_FACE_DETECTION_CONFIDENCE)
                    .setMinTrackingConfidence(MIN_FACE_TRACKING_CONFIDENCE)
                    .setMinFacePresenceConfidence(MIN_FACE_PRESENCE_CONFIDENCE)
                    .setNumFaces(MAX_NUM_FACES)
                    .setOutputFaceBlendshapes(true)
                    .setOutputFacialTransformationMatrixes(false)
                    .setRunningMode(RUNNING_MODE);

            optionsBuilder.setResultListener(this::postProcessLandmarks);

            options = optionsBuilder.build();
            faceLandmarker = FaceLandmarker.createFromOptions(this.context, options);

        } catch (IllegalStateException e) {
            Log.e(TAG, "MediaPipe failed to load the task with error: " + e.getMessage());
        } catch (RuntimeException e) {
            Log.e(TAG, "Face Landmarker failed to load model with error: " + e.getMessage());
        }
    }


    /**
     * Converts the ImageProxy to MP Image and feed it to Mediapipe Graph.
     * @param imageProxy An image proxy from camera feed
     */
    public void detectLiveStream(ImageProxy imageProxy) {

        // Reject new work if exceed limit.
        if (currentInWorks >= N_WORKS_LIMIT) {
            imageProxy.close();
            return;
        }

        // Reject new work if not ready.
        if (!isRunning || (faceLandmarker == null) || (imageProxy == null)) {
            return;
        }

        currentInWorks += 1;
        long startPreprocessTimeMs = SystemClock.uptimeMillis();

        frameWidth = imageProxy.getWidth();
        frameHeight = imageProxy.getHeight();


        Bitmap bitmap = Bitmap.createBitmap(frameWidth, frameHeight, Bitmap.Config.ARGB_8888);

        bitmap.copyPixelsFromBuffer(imageProxy.getPlanes()[0].getBuffer());

        // Handle rotations.
        Matrix rotationMatrix = getRotationMatrix(imageProxy);

        Bitmap rotatedBitmap =
            Bitmap.createBitmap(
                bitmap, 0, 0, imageProxy.getWidth(), imageProxy.getHeight(), rotationMatrix, true);

        // Convert the input Bitmap object to an MPImage object to run inference.
        MPImage mpImage = new BitmapImageBuilder(rotatedBitmap).build();

        try {
            faceLandmarker.detectAsync(mpImage, SystemClock.uptimeMillis());
        } catch (RuntimeException e) {
            Log.e(TAG, "Face Landmarker failed to detect async: " + e.getMessage());
        }

        imageProxy.close();

        // True input resolution for post.
        mpInputWidth = mpImage.getWidth();
        mpInputHeight = mpImage.getHeight();

        preprocessTimeMs = SystemClock.uptimeMillis() - startPreprocessTimeMs;

    }

    @NonNull
    private Matrix getRotationMatrix(ImageProxy imageProxy) {
        Matrix matrix = new Matrix();

        // Front camera rotation constant is 270 degrees.
        int matrixRotDegrees = frontCameraOrientation;
        int widthCorrected = imageProxy.getWidth();
        int heightCorrected = imageProxy.getHeight();
        float mpWidthCorrected = MP_WIDTH;
        float mpHeightCorrected = MP_HEIGHT;
        switch (currentRotationState) {
            case Surface.ROTATION_0:
                break;
            case Surface.ROTATION_90:
                matrixRotDegrees = frontCameraOrientation + 90;
                widthCorrected = imageProxy.getHeight();
                heightCorrected = imageProxy.getWidth();
                mpWidthCorrected = MP_HEIGHT;
                mpHeightCorrected = MP_WIDTH;
                break;
            case Surface.ROTATION_180:
                matrixRotDegrees = frontCameraOrientation + 180;
                widthCorrected = imageProxy.getWidth();
                heightCorrected = imageProxy.getHeight();
                mpWidthCorrected = MP_HEIGHT;
                mpHeightCorrected = MP_WIDTH;
                break;
            case Surface.ROTATION_270:
                matrixRotDegrees = frontCameraOrientation - 90;
                widthCorrected = imageProxy.getHeight();
                heightCorrected = imageProxy.getWidth();
                mpWidthCorrected = MP_HEIGHT;
                mpHeightCorrected = MP_WIDTH;
                break;
            default: // fall out
        }
        matrix.postRotate(matrixRotDegrees);
        matrix.postScale(-mpWidthCorrected / widthCorrected, mpHeightCorrected / heightCorrected);
        return matrix;
    }

    /**
     * Gets result landmarks and blendshapes then apply some scaling and save the value.
     *
     * @param result The result of face landmarker.
     * @param input The input image of face landmarker.
     */
    private void postProcessLandmarks(FaceLandmarkerResult result, MPImage input) {
        currentInWorks -= 1;
        mediapipeTimeMs = SystemClock.uptimeMillis() - result.timestampMs();
        input.close();

        if (!isRunning) {
            ensurePauseThread();
        }

        if (!result.faceLandmarks().isEmpty()) {
            isFaceVisible = true;
            currHeadX = result.faceLandmarks().get(0).get(FOREHEAD_INDEX).x() * mpInputWidth;
            currHeadY = result.faceLandmarks().get(0).get(FOREHEAD_INDEX).y() * mpInputHeight;

            if (result.faceBlendshapes().isPresent()) {
                // Convert from Category to simple float array.
                for (int i = 0; i < TOTAL_BLENDSHAPES; i++) {
                    currBlendshapes[i] = result.faceBlendshapes().get().get(0).get(i).score();
                }
            }

            timeSinceLastMeasurement = SystemClock.uptimeMillis() - lastMeasurementTsMs;
            lastMeasurementTsMs = SystemClock.uptimeMillis();
        } else {
            isFaceVisible = false;
        }

        long ts = SystemClock.uptimeMillis();
        gapTimeMs = ts - prevCallbackTimeMs;
        prevCallbackTimeMs = ts;
    }

    /** Get user's head X, Y coordinate in image space. */
    public float[] getHeadCoordXY() {
        return new float[] {currHeadX, currHeadY};
    }

    public float[] getBlendshapes() {

        return currBlendshapes;
    }

    /** Recreates {@link FaceLandmarker} and resume the process. */
    public void resumeThread() {
        faceLandmarker = FaceLandmarker.createFromOptions(this.context, options);
        isRunning = true;
    }


    /**
     * Completely pause the detection process.
     */
    public void pauseThread() {
        Log.i(TAG, "pauseThread");

        // There might be some image processing.
        isRunning = false;
        if (currentInWorks < 0) {
            ensurePauseThread();
        }
    }

    private void ensurePauseThread() {
        if (faceLandmarker != null) {
            faceLandmarker.close();
            faceLandmarker = null;
        }
    }

    /** Destroys {@link FaceLandmarker} and stop. */
    public void destroy() {
        Log.i(TAG, "destroy");
        isRunning = false;
        ensurePauseThread();
    }
}
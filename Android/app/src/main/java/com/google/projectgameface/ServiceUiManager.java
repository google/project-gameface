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
import static androidx.core.math.MathUtils.clamp;

import android.animation.ValueAnimator;
import android.annotation.SuppressLint;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.PixelFormat;
import android.graphics.Point;
import android.util.Log;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.view.WindowManager.LayoutParams;
import android.widget.Button;
import android.widget.ImageButton;
import androidx.camera.view.PreviewView;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.core.content.ContextCompat;

/**
 * Manage the interactive UI elements for {@link CursorAccessibilityService}. 1. Camera box: Shows
 * live video feed. 2. Cursor: Shows cursor image. 3. Fullscreen canvas: Draw drag line and drag
 * circle.
 */
public class ServiceUiManager {

  private static final String TAG = "ServiceUiManager";

  int avoidNavBarX = 0;
  int avoidNavBarY = 0;


  private static final boolean SHOW_DEBUG_TEXT = true;

  /** For applying small offset to cursor image.*/
  private static final int CURSOR_DP_SIZE = 60;

  Context parentContext;

  private final Point screenSize;

  /** Draw cursor image. */
  public View cursorView;

  /** Draw floating window that show video feed along with buttons and other information. */
  public View cameraBoxView;

  /** Button for maximize/minimize camera box. And also show status icon when in minimize state. */
  public ImageButton cameraBoxPopBtn;

  /** Open setting page. */
  public Button settingBtn;

  /** Realtime video feed from camera. */
  public PreviewView innerCameraImageView;

  /** Draw drag line hold radius circle on any place in the screen. */
  public View fullScreenCanvasView;



  public FullScreenCanvas fullScreenCanvas;

  /** Debug view that show preprocess frame time and MediaPipe frame time. */
  public CameraBoxOverlay cameraBoxOverlay;

  public FloatIconState nextIconState;
  public FloatIconState currentIconState = FloatIconState.MINIMIZE_ICON;

  // Float cam drag params
  private int floatCamMoveInitialX;
  private int floatCamMoveInitialY;
  private float initialTouchX;
  private float initialTouchY;


  /** Our cursor image is a circular so we
   * make a small shift to match the touch point at the center*/
  private final int shiftCursorImageX;
  private final int shiftCursorImageY;

  public static final int DEFAULT_FLOATING_CAMERA_WIDTH = 330;
  public static final int DEFAULT_FLOATING_CAMERA_HEIGHT = 330;



  Intent mainActivityIntent;

  private ValueAnimator flyAnim;
  public LayoutParams cursorLayoutParams;
  public LayoutParams cameraBoxLayoutParams;

  public LayoutParams fullScreenCanvasParams;

  private final int floatWindowFlags;
  private boolean cameraBoxDraggable = true;


  /** Icon that notify the state of the app. */
  public enum FloatIconState {
    FOUND_FACE_ICON,
    NO_FACE_ICON,
    MINIMIZE_ICON,
    PAUSE_ICON
  }

  WindowManager windowManager;

  /**
   * Create UI manager with given Accessibility service.
   *
   * @param context parent context.
   */
  public ServiceUiManager(Context context, WindowManager windowManager) {
    this.parentContext = context;
    this.windowManager = windowManager;

    screenSize = new Point();
    float density = parentContext.getResources().getDisplayMetrics().density;
    shiftCursorImageX = (int) (-CURSOR_DP_SIZE * density / 2);
    shiftCursorImageY = (int) (-CURSOR_DP_SIZE * density / 2);

    floatWindowFlags =
        LayoutParams.FLAG_DISMISS_KEYGUARD
            | LayoutParams.FLAG_HARDWARE_ACCELERATED
            | LayoutParams.FLAG_FULLSCREEN
            | LayoutParams.FLAG_NOT_TOUCHABLE
            | LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS
            | LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH
            | LayoutParams.FLAG_NOT_TOUCH_MODAL
            | LayoutParams.FLAG_NOT_FOCUSABLE
            | LayoutParams.FLAG_LAYOUT_IN_SCREEN
            | LayoutParams.FLAG_LAYOUT_NO_LIMITS;

    createFloatingCursor();
    createCameraBox();
    createFullScreenCanvas();
    fitCameraBoxToScreen();
  }

  /** Update status icon image by checking status of the service and face detector. */
  public void updateStatusIcon(boolean isPausing, boolean isFaceVisible) {
    switch (cameraBoxState) {
      case MINIMIZE:
        // If pause always show ⏸
        if (isPausing) {
          nextIconState = FloatIconState.PAUSE_ICON;
        } else {
          // Show face detector status.
          if (isFaceVisible) {
            nextIconState = FloatIconState.FOUND_FACE_ICON;
          } else {
            nextIconState = FloatIconState.NO_FACE_ICON;
          }
        }
        break;

      case MAXIMIZE:
        // In maximize mode only show the button to go minimize.
        nextIconState = FloatIconState.MINIMIZE_ICON;
        break;
    }

    // If nothing changed, no need to update.
    if (nextIconState == currentIconState) {
      return;
    }

    // Actually change the icon.
    switch (nextIconState) {
      case MINIMIZE_ICON:
        cameraBoxPopBtn.setImageResource(R.drawable.set_3_arrow);
        break;
      case FOUND_FACE_ICON:
        cameraBoxPopBtn.setImageResource(R.drawable.set_3_okay);
        break;
      case NO_FACE_ICON:
        cameraBoxPopBtn.setImageResource(R.drawable.set_3_warning);
        break;
      case PAUSE_ICON:
        cameraBoxPopBtn.setImageResource(R.drawable.set_3_paused);
        break;
    }
    currentIconState = nextIconState;
  }

  /** Create floating cursor image on the screen. */
  private void createFloatingCursor() {

    cursorView = View.inflate(parentContext, R.layout.cursor, null);


    cursorLayoutParams =
        new WindowManager.LayoutParams(
            LayoutParams.WRAP_CONTENT,
            LayoutParams.WRAP_CONTENT,
            LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
            floatWindowFlags,
            PixelFormat.TRANSLUCENT);
    cursorLayoutParams.gravity = Gravity.TOP | Gravity.START;
    cursorLayoutParams.x = screenSize.x / 2 - shiftCursorImageX ;
    cursorLayoutParams.y = screenSize.y / 2 - shiftCursorImageY ;


  }

  /** Hide cursor view. */
  public void hideCursor() {
    try {
      windowManager.removeView(cursorView);
    } catch (RuntimeException e) {
      Log.w(TAG, "windowManager failed to remove cursorView, might not been attached.");
    }
    nextIconState = FloatIconState.PAUSE_ICON;
  }

  /** Show cursor view. */
  public void showCursor() {
    try {
      windowManager.addView(cursorView, cursorLayoutParams);
    } catch (RuntimeException e) {
      Log.w(TAG, "windowManager failed to addView: " + e.getMessage());
    }
    nextIconState = FloatIconState.FOUND_FACE_ICON;
  }

  /** Create floating box that show camera feed along with buttons and other information. */
  @SuppressLint("ClickableViewAccessibility")
  private void createCameraBox() {
    cameraBoxView = View.inflate(parentContext, R.layout.floating_camera_layout, null);
    innerCameraImageView = cameraBoxView.findViewById(R.id.previewVideo);
    cameraBoxOverlay = cameraBoxView.findViewById(R.id.cameraBoxOverlay);

    cameraBoxLayoutParams =
        new LayoutParams(
            LayoutParams.WRAP_CONTENT,
            LayoutParams.WRAP_CONTENT,
            LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
            LayoutParams.FLAG_DISMISS_KEYGUARD
                | LayoutParams.FLAG_HARDWARE_ACCELERATED
                | LayoutParams.FLAG_FULLSCREEN
                | LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS
                | LayoutParams.FLAG_NOT_TOUCH_MODAL
                | LayoutParams.FLAG_LAYOUT_IN_SCREEN
                | LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH
                | LayoutParams.FLAG_NOT_FOCUSABLE
                | LayoutParams.FLAG_LAYOUT_IN_SCREEN
                | LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSLUCENT);

    cameraBoxLayoutParams.gravity = Gravity.TOP | Gravity.START;


    // Set touch listeners for dragging the window.
    cameraBoxView.setOnTouchListener(
        (v, event) -> {
          if (!cameraBoxDraggable) {
            return true;
          }
          switch (event.getAction()) {
            case MotionEvent.ACTION_DOWN:
              // Record the initial position and touch coordinates
              floatCamMoveInitialX = cameraBoxLayoutParams.x;
              floatCamMoveInitialY = cameraBoxLayoutParams.y;
              initialTouchX = event.getRawX();
              initialTouchY = event.getRawY();
              return true;
            case MotionEvent.ACTION_MOVE:
              // Calculate the new position based on touch movement
              cameraBoxLayoutParams.x =
                  clamp(
                      floatCamMoveInitialX + (int) (event.getRawX() - initialTouchX),
                      0,
                      screenSize.x - innerCameraImageView.getWidth());
              cameraBoxLayoutParams.y =
                  clamp(
                      floatCamMoveInitialY + (int) (event.getRawY() - initialTouchY),
                      0,
                      screenSize.y);

              // Update the window position
              windowManager.updateViewLayout(cameraBoxView, cameraBoxLayoutParams);
              return true;

            case MotionEvent.ACTION_UP:
              saveCameraBoxPosition(
                  "savedFloatCamXNorm",
                  (float) cameraBoxLayoutParams.x / (float) screenSize.x);
              saveCameraBoxPosition(
                  "savedFloatCamYNorm",
                  (float) cameraBoxLayoutParams.y / (float) screenSize.y);
              return true;

            default:
              return false;
          }
        });

    saveCameraBoxPosition(
        "savedFloatCamXNorm", (float) cameraBoxLayoutParams.x / screenSize.x);
    saveCameraBoxPosition(
        "savedFloatCamYNorm", (float) cameraBoxLayoutParams.y / screenSize.y);

    saveCameraBoxPosition("defaultWidth", DEFAULT_FLOATING_CAMERA_WIDTH);
    saveCameraBoxPosition("defaultHeight", DEFAULT_FLOATING_CAMERA_HEIGHT);

    settingBtn = cameraBoxView.findViewById(R.id.settingBtn);

    mainActivityIntent = new Intent(parentContext, MainActivity.class);
    mainActivityIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
    settingBtn.setOnClickListener(v -> parentContext.startActivity(mainActivityIntent));


    flyAnim = ValueAnimator.ofFloat(0f, 1f);

    cameraBoxPopBtn = cameraBoxView.findViewById(R.id.popBtn);
    cameraBoxPopBtn.setOnTouchListener(
        (view, event) -> {
          int action = event.getAction();
          switch (action) {
            case MotionEvent.ACTION_DOWN:
              // Record the initial position and touch coordinates
              floatCamMoveInitialX = cameraBoxLayoutParams.x;
              floatCamMoveInitialY = cameraBoxLayoutParams.y;
              initialTouchX = event.getRawX();
              initialTouchY = event.getRawY();
              break;

            // Drag on this button also move the whole camera box.
            case MotionEvent.ACTION_MOVE:

              // Clamp window x position in side screen.
              cameraBoxLayoutParams.x =
                  clamp(
                      floatCamMoveInitialX + (int) (event.getRawX() - initialTouchX),
                      /* min= */ 0,
                      /* max= */ screenSize.x - cameraBoxView.getWidth());

              // Clamp window y position in side screen.
              cameraBoxLayoutParams.y =
                  clamp(
                      floatCamMoveInitialY + (int) (event.getRawY() - initialTouchY),
                      /* min= */ 0,
                      /* max= */ screenSize.y);

              // Update the window position
              windowManager.updateViewLayout(cameraBoxView, cameraBoxLayoutParams);
              break;

            case MotionEvent.ACTION_UP:
              Log.i(TAG, "ACTION_UP: " + event.getRawX());

              // If release within 5 pixels, execute button function.
              if (Math.abs(event.getRawX() - initialTouchX) < 5
                  && Math.abs(event.getRawY() - initialTouchY) < 5) {

                // Toggle camera box.
                switch (cameraBoxState) {
                  case MAXIMIZE:
                    minimizeCameraBox();
                    break;
                  case MINIMIZE:
                    maximizeCameraBox();
                    break;
                }
                cameraBoxView.requestLayout();
              }
              break;

            default:
              break;
          }
          return true;
        });

    cameraBoxState = CameraBoxState.MAXIMIZE;
  }

  /** Should camera box draggable ? */
  public void setCameraBoxDraggable(boolean draggable) {
    cameraBoxDraggable = draggable;
  }

  public void hideCameraBox() {
    try {
      windowManager.removeView(cameraBoxView);
    } catch (RuntimeException e) {
      Log.w(TAG, "windowManager failed to remove floatCamView, might not attached.");
    }
  }

  public void showCameraBox() {
    updateScreenInfo();
    try {
      windowManager.addView(cameraBoxView, cameraBoxLayoutParams);
      resizeCameraBox(DEFAULT_FLOATING_CAMERA_WIDTH, DEFAULT_FLOATING_CAMERA_HEIGHT);
    } catch (RuntimeException e) {
      Log.w(TAG, "windowManager failed to add floatCamView: " + e.getMessage());
    }
  }

  /** Force camera box to show up. */
  public void showAllWindows() {
    fitCameraBoxToScreen();

    showCameraBox();
    showFullscreenCanvas();
    showCursor();
    maximizeCameraBox();
  }

  public void hideAllWindows() {
    hideCameraBox();
    hideCursor();
    hideFullscreenCanvas();
  }

  /** This enum represents the state of camera. */
  public enum CameraBoxState {
    MAXIMIZE,
    MINIMIZE
  }

  public CameraBoxState cameraBoxState;

  public void maximizeCameraBox() {
    Log.i(TAG, "maximizeCameraBox");
    cameraBoxView.findViewById(R.id.previewVideo).setVisibility(View.VISIBLE);
    settingBtn.setVisibility(View.VISIBLE);
    resizeCameraBox(DEFAULT_FLOATING_CAMERA_WIDTH, DEFAULT_FLOATING_CAMERA_HEIGHT);

    cameraBoxView.findViewById(R.id.popBtn).setBackground(null);
    cameraBoxOverlay.setVisibility(View.VISIBLE);
    cameraBoxState = CameraBoxState.MAXIMIZE;
  }

  public void minimizeCameraBox() {
    Log.i(TAG, "minimizeCameraBox");
    cameraBoxView.findViewById(R.id.previewVideo).setVisibility(View.GONE);
    settingBtn.setVisibility(View.GONE);
    resizeCameraBox(cameraBoxPopBtn.getWidth(), cameraBoxPopBtn.getHeight());
    cameraBoxOverlay.setBackground(null);
    cameraBoxOverlay.setVisibility(View.INVISIBLE);
    cameraBoxView
        .findViewById(R.id.popBtn)
        .setBackground(ContextCompat.getDrawable(parentContext, R.drawable.custom_imagebtn_camera));
    cameraBoxState = CameraBoxState.MINIMIZE;
  }

  /** Fly floatCamView to target location */
  private void playFlyCameraBoxAnimation(int targetX, int targetY, int duration) {
    Log.i(TAG, "playFlyCameraBoxAnimation: ");

    int startX = cameraBoxLayoutParams.x;
    int startY = cameraBoxLayoutParams.y;
    flyAnim.setDuration(duration);
    flyAnim.addUpdateListener(
        animation -> {
          // In each frame.
          float fraction = animation.getAnimatedFraction();
          int currentX = (int) (startX + fraction * (targetX - startX));
          int currentY = (int) (startY + fraction * (targetY - startY));
          cameraBoxLayoutParams.x = currentX;
          cameraBoxLayoutParams.y = currentY;

          try {
            windowManager.updateViewLayout(cameraBoxView, cameraBoxLayoutParams);
          } catch (RuntimeException e) {
            Log.w(TAG, "windowManager failed to update floatCamView: " + e.getMessage());
          }
        });

    flyAnim.start();
  }

  public void resizeCameraBox(int width, int height) {
    ViewGroup.LayoutParams layoutParams = new ConstraintLayout.LayoutParams(width, height);
    innerCameraImageView.setLayoutParams(layoutParams);
    cameraBoxLayoutParams.width = width;
    cameraBoxLayoutParams.height = height;

    try {
      windowManager.updateViewLayout(cameraBoxView, cameraBoxLayoutParams);
    } catch (RuntimeException e) {
      Log.w(TAG, "windowManager failed to update floatCamView: " + e.getMessage());
    }
  }

  private void createFullScreenCanvas() {
    fullScreenCanvasView = View.inflate(parentContext, R.layout.fullscreen_canvas, null);
    fullScreenCanvas = fullScreenCanvasView.findViewById(R.id.fullscreenCanvasInner);



    fullScreenCanvasParams =
        new LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.WRAP_CONTENT,
            LayoutParams.TYPE_ACCESSIBILITY_OVERLAY,
            LayoutParams.FLAG_DISMISS_KEYGUARD
                | LayoutParams.FLAG_HARDWARE_ACCELERATED
                | LayoutParams.FLAG_FULLSCREEN
                | LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS
                | LayoutParams.FLAG_NOT_TOUCH_MODAL
                | LayoutParams.FLAG_NOT_TOUCHABLE
                | LayoutParams.FLAG_LAYOUT_IN_SCREEN
                | LayoutParams.FLAG_WATCH_OUTSIDE_TOUCH
                | LayoutParams.FLAG_NOT_FOCUSABLE
                | LayoutParams.FLAG_LAYOUT_NO_LIMITS,
            PixelFormat.TRANSPARENT);

    fullScreenCanvasParams.gravity = Gravity.TOP | Gravity.START;
    fullScreenCanvas.bringToFront();


  }

  private void showFullscreenCanvas() {
    try {
      windowManager.addView(fullScreenCanvasView, fullScreenCanvasParams);
    } catch (RuntimeException e) {
      Log.w(TAG, "windowManager failed to add fullScreenCanvasView: " + e.getMessage());
    }
  }

  private void hideFullscreenCanvas() {
    try {
      windowManager.removeView(fullScreenCanvasView);
    } catch (RuntimeException e) {
      Log.w(TAG, "windowManager failed to remove fullScreenCanvasView, might not attached.");
    }
  }

  /** Save default camera box position to make it persistent when open the app. */
  private void saveCameraBoxPosition(String key, float value) {
    Log.i(TAG, "saveDefaultPosition: " + key + " " + value);
    SharedPreferences preferences =
        parentContext.getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
    SharedPreferences.Editor editor = preferences.edit();
    editor.putFloat(key, value);
    editor.apply();
  }


  /**
   * Change cursor image on screen.
   */
  public void updateCursorImagePositionOnScreen(
      int[] cursorPosition) {

    cursorLayoutParams.x = cursorPosition[0] + shiftCursorImageX;// + avoidNavBarX;
    cursorLayoutParams.y = cursorPosition[1] + shiftCursorImageY;// + avoidNavBarY;

    try {
      windowManager.updateViewLayout(cursorView, cursorLayoutParams);
      cursorView.requestLayout();
    } catch (RuntimeException e) {
      Log.w(TAG, "updateCursorImagePositionOnScreen: " + e.getMessage());
    }


  }

  public void setDragLineStart(float x, float y) {
    fullScreenCanvas.setDragLineStart(x + avoidNavBarX,y+avoidNavBarY);
  }

  public void updateDragLine(int[] cursorPosition) {
    fullScreenCanvas.updateDragLine(
        cursorPosition[0] + avoidNavBarX,
        cursorPosition[1] + avoidNavBarY);
  }

  /**
   * If {@value SHOW_DEBUG_TEXT}, Update the information overlay on camera box.
   *
   * @param preprocessValue Time of the image preprocessing.
   * @param mediapipeValue Time of the MediaPipe processing.
   */
  public void updateDebugTextOverlay(long preprocessValue, long mediapipeValue, boolean isPausing) {
    if (SHOW_DEBUG_TEXT) {
      cameraBoxOverlay.setOverlayInfo(preprocessValue, mediapipeValue);
      cameraBoxOverlay.setPauseIndicator(isPausing);
    }
  }

  /**
   * Draw white dot on the user head.
   *
   * @param headCoord Head coordinate x, y.
   * @param mpImageWidth MediaPipe's image width for normalization.
   * @param mpImageHeight MediaPipe's image height for normalization.
   */
  public void drawHeadCenter(float[] headCoord, int mpImageWidth, int mpImageHeight) {
    cameraBoxOverlay.setWhiteDot(
        headCoord[0] * innerCameraImageView.getWidth() / mpImageWidth,
        headCoord[1] * innerCameraImageView.getHeight() / mpImageHeight);
  }

  /** Fly camera box to screen center and hide all buttons (for setting page. ). */
  public BroadcastReceiver flyInWindowReceiver =
      new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
          Log.i(TAG, "flyInWindowReceiver");

          if (cameraBoxState == CameraBoxState.MINIMIZE) {
            maximizeCameraBox();
          }

          int positionX = intent.getIntExtra("positionX", 0);
          int positionY = intent.getIntExtra("positionY", 0);
          int width = intent.getIntExtra("width", 0);
          int height = intent.getIntExtra("height", 0);
          playFlyCameraBoxAnimation(positionX, positionY, 300);
          resizeCameraBox(width, height);

          cameraBoxView.findViewById(R.id.popBtn).setBackground(null);
          cameraBoxView.findViewById(R.id.popBtn).setVisibility(View.INVISIBLE);
          cameraBoxView.findViewById(R.id.settingBtn).setVisibility(View.INVISIBLE);
          cameraBoxOverlay.setVisibility(View.INVISIBLE);
        }
      };

  /** Fly out to the screen edge. */
  public BroadcastReceiver flyOutWindowReceiver =
      new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
          SharedPreferences preferences =
              parentContext.getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
          float positionX =
              preferences.getFloat(
                  "savedFloatCamXNorm",
                  (float) cameraBoxLayoutParams.x / (float) screenSize.x)
                  * screenSize.x;
          float positionY =
              preferences.getFloat(
                  "savedFloatCamYNorm",
                  (float) cameraBoxLayoutParams.y / (float) screenSize.y)
                  * screenSize.y;

          float width = preferences.getFloat("defaultWidth", 0);
          float height = preferences.getFloat("defaultHeight", 0);
          resizeCameraBox((int) width, (int) height);

          playFlyCameraBoxAnimation((int) positionX, (int) positionY, 300);
          cameraBoxView.findViewById(R.id.popBtn).setVisibility(View.VISIBLE);
          cameraBoxView.findViewById(R.id.settingBtn).setVisibility(View.VISIBLE);
        }
      };



  /** Draw small green dot where the touch event occur. */
  public void drawTouchDot(int[] cursorPositionXY) {
    fullScreenCanvas.drawTouchCircle(
        cursorPositionXY[0] + avoidNavBarX,
        cursorPositionXY[1] + avoidNavBarY
        );


  }


  private void updateScreenInfo()
  {
    if (windowManager == null) {
      return;
    }

    // Check new screen size and rotation.
    windowManager.getDefaultDisplay().getRealSize(screenSize);
  }

  /** Move camera box inside the screen. */
  public void fitCameraBoxToScreen() {


    updateScreenInfo();

    // Update the camera box location
    // so it not going out of screen when rotate device.
    SharedPreferences preferences =
        parentContext.getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
    cameraBoxLayoutParams.x =
        (int)
            (preferences.getFloat(
                "savedFloatCamXNorm",
                (float) cameraBoxLayoutParams.x / (float) screenSize.x)
                * screenSize.x);
    cameraBoxLayoutParams.y =
        (int)
            (preferences.getFloat(
                "savedFloatCamYNorm",
                (float) cameraBoxLayoutParams.y / (float) screenSize.y)
                * screenSize.y);
    try {
      windowManager.updateViewLayout(cameraBoxView, cameraBoxLayoutParams);
    } catch (RuntimeException e) {
      Log.w(TAG, "WindowManager failed to update view layout: " + e.getMessage());
    }

    if (cameraBoxState == CameraBoxState.MINIMIZE) {
      maximizeCameraBox();
    }
  }




}
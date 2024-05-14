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

import android.view.MenuItem;
import android.view.ViewTreeObserver;
import android.view.WindowManager.LayoutParams;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.res.ResourcesCompat;
import androidx.core.math.MathUtils;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
import com.google.projectgameface.CursorAccessibilityService.ServiceState;

import java.util.Objects;

public class GestureSizeActivity extends AppCompatActivity {

    private static final String TAG = "GestureSizeActivity";
    BroadcastReceiver stateReceiver;
    BroadcastReceiver scoreReceiver;
    private boolean isServicePreviouslyEnabled = false;

    private ProgressBar progressBar;

    private int thresholdInUi;


    private final int seekBarDefaultValue = 2;
    private static final int SEEK_BAR_MAXIMUM_VALUE = 10;
    private static final int SEEK_BAR_MINIMUM_VALUE = 0;

    private static final int SEEK_BAR_LOW_CLIP = 10;
    private static final int SEEK_BAR_HIGH_CLIP = 100;
    private LinearLayout cameraBoxPlaceHolder;

    private Boolean isPlaceHolderLaidOut = false;

    protected int getSeekBarDefaultValue() {
        return seekBarDefaultValue;
    }




    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_gesture_size);
        getWindow().addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON);

        SharedPreferences preferences = getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);


        BlendshapeEventTriggerConfig.EventType pageEventType = (BlendshapeEventTriggerConfig.EventType) getIntent().getSerializableExtra("eventType");
        BlendshapeEventTriggerConfig.Blendshape selectedGesture = (BlendshapeEventTriggerConfig.Blendshape) getIntent().getSerializableExtra("selectedGesture");
        if (selectedGesture == null || pageEventType == null)
        {
            Log.e(TAG, "Start intent with invalid extras.");
            finish();
            return;
        }
        Log.i(TAG, "onCreate: " + pageEventType + " " + selectedGesture);

        //setting actionbar
        Objects.requireNonNull(getSupportActionBar()).setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setTitle("Adjust gesture sensitivity");

        //Check if service is enabled.
        checkIfServiceEnabled();

        scorePreview(true, selectedGesture.toString());

        SeekBar gestureSizeSeekBar = findViewById(R.id.gestureSizeSeekBar);
        thresholdInUi = preferences.getInt(pageEventType +"_size", seekBarDefaultValue * 10);
        thresholdInUi = MathUtils.clamp(thresholdInUi, SEEK_BAR_LOW_CLIP, SEEK_BAR_HIGH_CLIP);
        gestureSizeSeekBar.setMax(SEEK_BAR_MAXIMUM_VALUE);
        gestureSizeSeekBar.setMin(SEEK_BAR_MINIMUM_VALUE);
        gestureSizeSeekBar.setProgress(thresholdInUi / 10);

        TextView targetGesture = findViewById(R.id.targetGesture);

        String beautifyBlendshapeName = BlendshapeEventTriggerConfig.BEAUTIFY_BLENDSHAPE_NAME.get(selectedGesture);
        targetGesture.setText("Perform \""+beautifyBlendshapeName+"\"");


        stateReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                int stateIndex = intent.getIntExtra("state", CursorAccessibilityService.ServiceState.DISABLE.ordinal());
              isServicePreviouslyEnabled =
                  Objects.requireNonNull(ServiceState.values()[stateIndex]) != ServiceState.DISABLE;
            }
        };

        scoreReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                int progress = (int)(intent.getFloatExtra("score", 0.0f)*100);
                if(progress > thresholdInUi){
                    progressBar.setProgressDrawable(ResourcesCompat.getDrawable(getResources(),R.drawable.custom_progress, null));
                } else {
                    progressBar.setProgressDrawable(ResourcesCompat.getDrawable(getResources(),R.drawable.custom_progress_threshold,null));
                }
                progressBar.setProgress(progress);
            }
        };

        cameraBoxPlaceHolder = findViewById(R.id.cameraBoxPlaceHolder);

        // Move camera window to match the cameraBoxPlaceHolder in the layout.
        cameraBoxPlaceHolder.getViewTreeObserver().addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
            @Override
            public void onGlobalLayout() {
                isPlaceHolderLaidOut = true;
                int[] locationOnScreen = new int[2];
                cameraBoxPlaceHolder.getLocationOnScreen(locationOnScreen);
                  fitCameraBoxToPlaceHolder(locationOnScreen[0], locationOnScreen[1],
                          cameraBoxPlaceHolder.getWidth(), cameraBoxPlaceHolder.getHeight());

                cameraBoxPlaceHolder.getViewTreeObserver().removeOnGlobalLayoutListener(this);
            }
        });

        findViewById(R.id.Bigger).setOnClickListener(v -> {
            int currentValue = gestureSizeSeekBar.getProgress();
            int newValue = currentValue+1;
            if(newValue<11){
                thresholdInUi = newValue*10;
                gestureSizeSeekBar.setProgress(newValue);
            }
        });

        findViewById(R.id.Smaller).setOnClickListener(v -> {
            int currentValue = gestureSizeSeekBar.getProgress();
            int newValue = currentValue - 1;
            if(newValue>-1){
                thresholdInUi = newValue * 10;
                gestureSizeSeekBar.setProgress(newValue);
            }
        });

        findViewById(R.id.doneBtn).setOnClickListener(v -> {
            BlendshapeEventTriggerConfig.writeBindingConfig(getBaseContext(), selectedGesture, pageEventType,
                thresholdInUi);
            try {
                CharSequence text = "Setting Completed!";
                int duration = Toast.LENGTH_LONG;
                Toast toast = Toast.makeText(getBaseContext(), text, duration);
                toast.show();
            } catch (Exception e) {
                Log.i(TAG, e.toString());
            }
            // Go back to cursor binding page.
            Intent intent = new Intent(this, CursorBinding.class);
            startActivity(intent);

            restorePreviousServiceState();
            finish();


        });

        findViewById(R.id.backBtn).setOnClickListener(v -> {
                    finish();
        });



        gestureSizeSeekBar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                // Prevent user from set the threshold to 0.
                if (progress == 0) {
                    seekBar.setProgress(1);
                }
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {

            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                thresholdInUi = seekBar.getProgress() * 10;
            }
        });

        progressBar = findViewById(R.id.gestureSizeBar);
        registerReceiver(scoreReceiver, new IntentFilter(selectedGesture.toString()),RECEIVER_EXPORTED);
        registerReceiver(stateReceiver, new IntentFilter("SERVICE_STATE_GESTURE"),RECEIVER_EXPORTED);
    }

    private void fitCameraBoxToPlaceHolder(int placeholderX, int placeholderY,
                                           int placeHolderWidth, int placeHolderHeight) {

        // Temporary change to GLOBAL_STICK state.
        Intent intentChangeServiceState = new Intent("CHANGE_SERVICE_STATE");
        intentChangeServiceState.putExtra("state", ServiceState.GLOBAL_STICK.ordinal());
        sendBroadcast(intentChangeServiceState);


        Intent intentFlyIn = new Intent("FLY_IN_FLOAT_WINDOW");
        intentFlyIn.putExtra("positionX", placeholderX);
        intentFlyIn.putExtra("positionY", placeholderY);
        intentFlyIn.putExtra("width", placeHolderWidth);
        intentFlyIn.putExtra("height", placeHolderHeight);
        sendBroadcast(intentFlyIn);
    }

    public void checkIfServiceEnabled() {
        // send broadcast to service to check its state.
        Intent intent = new Intent("REQUEST_SERVICE_STATE");
        intent.putExtra("state","gesture");
        sendBroadcast(intent);
    }

    private void scorePreview(boolean status, String requestedScoreName) {
        Intent intent = new Intent("ENABLE_SCORE_PREVIEW");
        intent.putExtra("enable", status);
        intent.putExtra("blendshapesName", requestedScoreName);
        sendBroadcast(intent);
    }


    private void restorePreviousServiceState() {

        // Resume the previous service state.
        if(isServicePreviouslyEnabled){
            Intent intentChangeServiceState = new Intent("CHANGE_SERVICE_STATE");
            intentChangeServiceState.putExtra("state", CursorAccessibilityService.ServiceState.ENABLE.ordinal());
            sendBroadcast(intentChangeServiceState);
        }
        else{
            Intent intentPreviewCameraMode = new Intent("CHANGE_SERVICE_STATE");
            intentPreviewCameraMode.putExtra("state", CursorAccessibilityService.ServiceState.DISABLE.ordinal());
            sendBroadcast(intentPreviewCameraMode);
        }
    }


    @Override
    protected void onResume() {
        super.onResume();

        if (!isPlaceHolderLaidOut){
            return;
        }

        int[] locationOnScreen = new int[2];
        cameraBoxPlaceHolder.getLocationOnScreen(locationOnScreen);
        fitCameraBoxToPlaceHolder(locationOnScreen[0], locationOnScreen[1],
                cameraBoxPlaceHolder.getWidth(), cameraBoxPlaceHolder.getHeight());


    }

    @Override
    protected void onPause() {
        super.onPause();
        scorePreview(false, null);
        try {
            unregisterReceiver(scoreReceiver);
        } catch (Exception ignored){

        }
        restorePreviousServiceState();
    }



    /**
     * Make back button work as back action in device's navigation.
     * @param item The menu item that was selected.
     */
    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
        if (item.getItemId() == android.R.id.home) {
            finish();
            return true;
        }
        return super.onOptionsItemSelected(item);

    }

}
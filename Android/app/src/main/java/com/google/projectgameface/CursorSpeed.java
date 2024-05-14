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

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.WindowManager.LayoutParams;
import androidx.appcompat.app.AppCompatActivity;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.SeekBar;
import android.widget.TextView;

import com.google.projectgameface.R;

import java.util.Objects;

/** The cursor speed activity of Gameface app. */
public class CursorSpeed extends AppCompatActivity {

    protected static final int SEEK_BAR_MAXIMUM_VALUE = 10;

    protected static final int SEEK_BAR_MINIMUM_VALUE = 0;

    private TextView textViewMu; // Show move up speed value.
    private TextView textViewMd; // Show move down speed value.
    private TextView textViewMr; // Show move right speed value.
    private TextView textViewMl; // Show move left speed value.
    private TextView textViewSmoothPointer; // Show the smoothness value of the cursor.
    private TextView textViewBlendshapes; // Show flickering of the a trigger.
    private TextView textViewDelay; // Show the how long the user should hold a gesture value.

    private SeekBar seekBarMu; // Move up speed.
    private SeekBar seekBarMd; // Move down speed.
    private SeekBar seekBarMr; // Move right speed.
    private SeekBar seekBarMl; // Move left speed.
    private SeekBar seekBarSmoothPointer; // The smoothness of the cursor.
    private SeekBar seekBarBlendshapes; // The flickering of the a trigger.
    private SeekBar seekBarDelay; // Controls how long the user should hold a gesture.

    private final int[] viewIds = {
        R.id.fasterUp,
        R.id.slowerUp,
        R.id.fasterDown,
        R.id.slowerDown,
        R.id.fasterRight,
        R.id.slowerRight,
        R.id.fasterLeft,
        R.id.slowerLeft,
        R.id.fasterPointer,
        R.id.slowerPointer,
        R.id.fasterBlendshapes,
        R.id.slowerBlendshapes,
        R.id.fasterDelay,
        R.id.slowerDelay
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cursor_speed);
        getWindow().addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON);

        // setting actionbar
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setTitle("Adjust cursor speed");

        // SeekBar Binding and Textview Progress
        seekBarMu = (SeekBar) findViewById(R.id.seekBarMU);
        textViewMu = findViewById(R.id.progressMU);
        setUpSeekBarAndTextView(
            seekBarMu, textViewMu, String.valueOf(CursorMovementConfig.CursorMovementConfigType.UP_SPEED));

        seekBarMd = (SeekBar) findViewById(R.id.seekBarMD);
        textViewMd = findViewById(R.id.progressMD);
        setUpSeekBarAndTextView(
            seekBarMd, textViewMd, String.valueOf(CursorMovementConfig.CursorMovementConfigType.DOWN_SPEED));

        seekBarMr = (SeekBar) findViewById(R.id.seekBarMR);
        textViewMr = findViewById(R.id.progressMR);
        setUpSeekBarAndTextView(
            seekBarMr, textViewMr, String.valueOf(CursorMovementConfig.CursorMovementConfigType.RIGHT_SPEED));

        seekBarMl = (SeekBar) findViewById(R.id.seekBarML);
        textViewMl = findViewById(R.id.progressML);
        setUpSeekBarAndTextView(
            seekBarMl, textViewMl, String.valueOf(CursorMovementConfig.CursorMovementConfigType.LEFT_SPEED));

        seekBarSmoothPointer = (SeekBar) findViewById(R.id.seekBarSmoothPointer);
        textViewSmoothPointer = findViewById(R.id.progressSmoothPointer);
        setUpSeekBarAndTextView(
            seekBarSmoothPointer,
            textViewSmoothPointer,
            String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_POINTER));

        seekBarBlendshapes = (SeekBar) findViewById(R.id.seekBarBlendshapes);
        textViewBlendshapes = findViewById(R.id.progressBlendshapes);
        setUpSeekBarAndTextView(
            seekBarBlendshapes,
            textViewBlendshapes,
            String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_BLENDSHAPES));

        seekBarDelay = (SeekBar) findViewById(R.id.seekBarDelay);
        textViewDelay = findViewById(R.id.progressDelay);
        setUpSeekBarAndTextView(
            seekBarDelay, textViewDelay, String.valueOf(CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS));

        // Binding buttons.
        for (int id : viewIds) {
            findViewById(id).setOnClickListener(buttonClickListener);
        }
    }

    private void setUpSeekBarAndTextView(SeekBar seekBar, TextView textView, String preferencesId) {
        seekBar.setMax(SEEK_BAR_MAXIMUM_VALUE);
        seekBar.setMin(SEEK_BAR_MINIMUM_VALUE);
        SharedPreferences preferences = getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
        int savedProgress;
        if (Objects.equals(preferencesId, CursorMovementConfig.CursorMovementConfigType.SMOOTH_POINTER.toString())) {
            savedProgress = preferences.getInt(preferencesId, CursorMovementConfig.InitialRawValue.SMOOTH_POINTER);
        } else if (Objects.equals(preferencesId, CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS.toString())) {
            savedProgress = preferences.getInt(preferencesId, CursorMovementConfig.InitialRawValue.HOLD_TIME_MS);
        } else {
            savedProgress = preferences.getInt(preferencesId, CursorMovementConfig.InitialRawValue.DEFAULT_SPEED);
        }
        seekBar.setProgress(savedProgress);
        seekBar.setOnSeekBarChangeListener(seekBarChange);
        if (Objects.equals(preferencesId, CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS.toString())) {
            int timeMsForShow = (int) (savedProgress * CursorMovementConfig.RawConfigMultiplier.HOLD_TIME_MS);
            textView.setText(String.valueOf(timeMsForShow));
        } else {
            textView.setText(String.valueOf(savedProgress));
        }
    }

    private void sendValueToService(String configName, int value) {
        saveCursorSpeed(configName, value);
        Intent intent = new Intent("LOAD_SHARED_CONFIG_BASIC");
        intent.putExtra("configName", configName);
        sendBroadcast(intent);
    }

    private View.OnClickListener buttonClickListener =
        new OnClickListener() {
            @Override
            public void onClick(View v) {
                int currentValue;
                int newValue = 0;
                boolean isFaster = true; // False means slower
                String valueName = "";
                if (v.getId() == R.id.fasterUp) {
                    currentValue = seekBarMu.getProgress();
                    newValue = currentValue + 1;
                    isFaster = true;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.UP_SPEED);
                } else if (v.getId() == R.id.slowerUp) {
                    currentValue = seekBarMu.getProgress();
                    newValue = currentValue - 1;
                    isFaster = false;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.UP_SPEED);
                } else if (v.getId() == R.id.fasterDown) {
                    currentValue = seekBarMd.getProgress();
                    newValue = currentValue + 1;
                    isFaster = true;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.DOWN_SPEED);
                } else if (v.getId() == R.id.slowerDown) {
                    currentValue = seekBarMd.getProgress();
                    newValue = currentValue - 1;
                    isFaster = false;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.DOWN_SPEED);
                } else if (v.getId() == R.id.fasterRight) {
                    currentValue = seekBarMr.getProgress();
                    newValue = currentValue + 1;
                    isFaster = true;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.RIGHT_SPEED);
                } else if (v.getId() == R.id.slowerRight) {
                    currentValue = seekBarMr.getProgress();
                    newValue = currentValue - 1;
                    isFaster = false;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.RIGHT_SPEED);
                } else if (v.getId() == R.id.fasterLeft) {
                    currentValue = seekBarMl.getProgress();
                    newValue = currentValue + 1;
                    isFaster = true;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.LEFT_SPEED);
                } else if (v.getId() == R.id.slowerLeft) {
                    currentValue = seekBarMl.getProgress();
                    newValue = currentValue - 1;
                    isFaster = false;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.LEFT_SPEED);
                } else if (v.getId() == R.id.fasterPointer) {
                    currentValue = seekBarSmoothPointer.getProgress();
                    newValue = currentValue + 1;
                    isFaster = true;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_POINTER);
                } else if (v.getId() == R.id.slowerPointer) {
                    currentValue = seekBarSmoothPointer.getProgress();
                    newValue = currentValue - 1;
                    isFaster = false;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_POINTER);
                } else if (v.getId() == R.id.fasterBlendshapes) {
                    currentValue = seekBarBlendshapes.getProgress();
                    newValue = currentValue + 1;
                    isFaster = true;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_BLENDSHAPES);
                } else if (v.getId() == R.id.slowerBlendshapes) {
                    currentValue = seekBarBlendshapes.getProgress();
                    newValue = currentValue - 1;
                    isFaster = false;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_BLENDSHAPES);
                } else if (v.getId() == R.id.fasterDelay) {
                    currentValue = seekBarDelay.getProgress();
                    newValue = currentValue + 1;
                    isFaster = true;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS);
                } else if (v.getId() == R.id.slowerDelay) {
                    currentValue = seekBarDelay.getProgress();
                    newValue = currentValue - 1;
                    isFaster = false;
                    valueName = String.valueOf(CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS);
                }
                if ((isFaster && newValue < 11) || (!isFaster && newValue > -1)) {
                    if (Objects.equals(valueName, CursorMovementConfig.CursorMovementConfigType.UP_SPEED.toString())) {
                        seekBarMu.setProgress(newValue);
                        sendValueToService(valueName, newValue);
                    } else if (Objects.equals(valueName, CursorMovementConfig.CursorMovementConfigType.DOWN_SPEED.toString())) {
                        seekBarMd.setProgress(newValue);
                        sendValueToService(valueName, newValue);
                    } else if (Objects.equals(valueName, CursorMovementConfig.CursorMovementConfigType.RIGHT_SPEED.toString())) {
                        seekBarMr.setProgress(newValue);
                        sendValueToService(valueName, newValue);
                    } else if (Objects.equals(valueName, CursorMovementConfig.CursorMovementConfigType.LEFT_SPEED.toString())) {
                        seekBarMl.setProgress(newValue);
                        sendValueToService(valueName, newValue);
                    } else if (Objects.equals(valueName, CursorMovementConfig.CursorMovementConfigType.SMOOTH_POINTER.toString())) {
                        seekBarSmoothPointer.setProgress(newValue);
                        sendValueToService(valueName, newValue);
                    } else if (Objects.equals(valueName, CursorMovementConfig.CursorMovementConfigType.SMOOTH_BLENDSHAPES.toString())) {
                        seekBarBlendshapes.setProgress(newValue);
                        sendValueToService(valueName, newValue);
                    } else if (Objects.equals(valueName, CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS.toString())) {
                        seekBarDelay.setProgress(newValue);
                        sendValueToService(valueName, newValue);
                    }
                }
            }
        };

    private SeekBar.OnSeekBarChangeListener seekBarChange =
        new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                if (seekBar.getId() == R.id.seekBarMU) {
                    textViewMu.setText(String.valueOf(progress));
                } else if (seekBar.getId() == R.id.seekBarMD) {
                    textViewMd.setText(String.valueOf(progress));
                } else if (seekBar.getId() == R.id.seekBarMR) {
                    textViewMr.setText(String.valueOf(progress));
                } else if (seekBar.getId() == R.id.seekBarML) {
                    textViewMl.setText(String.valueOf(progress));
                } else if (seekBar.getId() == R.id.seekBarSmoothPointer) {
                    textViewSmoothPointer.setText(String.valueOf(progress));
                } else if (seekBar.getId() == R.id.seekBarBlendshapes) {
                    textViewBlendshapes.setText(String.valueOf(progress));
                } else if (seekBar.getId() == R.id.seekBarDelay) {
                    int timeMsForShow = (int) (progress * CursorMovementConfig.RawConfigMultiplier.HOLD_TIME_MS);
                    textViewDelay.setText(String.valueOf(timeMsForShow));
                }
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {}

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                if (seekBar.getId() == R.id.seekBarMU) {
                    sendValueToService(
                        String.valueOf(CursorMovementConfig.CursorMovementConfigType.UP_SPEED), seekBar.getProgress());
                } else if (seekBar.getId() == R.id.seekBarMD) {
                    sendValueToService(
                        String.valueOf(CursorMovementConfig.CursorMovementConfigType.DOWN_SPEED), seekBar.getProgress());
                } else if (seekBar.getId() == R.id.seekBarMR) {
                    sendValueToService(
                        String.valueOf(CursorMovementConfig.CursorMovementConfigType.RIGHT_SPEED), seekBar.getProgress());
                } else if (seekBar.getId() == R.id.seekBarML) {
                    sendValueToService(
                        String.valueOf(CursorMovementConfig.CursorMovementConfigType.LEFT_SPEED), seekBar.getProgress());
                } else if (seekBar.getId() == R.id.seekBarSmoothPointer) {
                    sendValueToService(
                        String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_POINTER), seekBar.getProgress());
                } else if (seekBar.getId() == R.id.seekBarBlendshapes) {
                    sendValueToService(
                        String.valueOf(CursorMovementConfig.CursorMovementConfigType.SMOOTH_BLENDSHAPES), seekBar.getProgress());
                } else if (seekBar.getId() == R.id.seekBarDelay) {
                    sendValueToService(
                        String.valueOf(CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS), seekBar.getProgress());
                }
            }
        };

    private void saveCursorSpeed(String key, int value) {
        SharedPreferences preferences = getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
        SharedPreferences.Editor editor = preferences.edit();
        editor.putInt(key, value);
        editor.apply();
    }
}
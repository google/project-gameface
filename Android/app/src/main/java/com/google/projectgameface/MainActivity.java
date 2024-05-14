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


import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.pm.PackageManager.NameNotFoundException;
import android.os.Bundle;
import android.provider.Settings;
import android.text.TextUtils;
import android.util.Log;
import android.view.WindowManager.LayoutParams;
import android.widget.Button;
import android.widget.Switch;
import android.widget.TextView;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;
import androidx.core.app.ActivityCompat;
import androidx.core.splashscreen.SplashScreen;

public class MainActivity extends AppCompatActivity {

    private static final int CAMERA_PERMISSION_CODE = 200;
    private static final String KEY_FIRST_RUN = "GameFaceFirstRun";

    private final String TAG = "MainActivity";

    private Intent cursorServiceIntent;

    private SharedPreferences preferences;
    private boolean isServiceBound = false;
    private boolean keep = true;



    @Override
    protected void onCreate(Bundle savedInstanceState) {

        // Handle the splash screen transition.
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);
        super.onCreate(savedInstanceState);


        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM);
        setContentView(R.layout.activity_main);
        getWindow().addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON);

        preferences = getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
        try {
            TextView versionNumber = findViewById(R.id.versionNumber);
            String versionName = getApplicationContext().getPackageManager().getPackageInfo(getApplicationContext().getPackageName(), 0 ).versionName;
            versionNumber.setText(versionName);
        } catch (NameNotFoundException e) {
            throw new RuntimeException(e);
        }



        if (getSupportActionBar() != null) {
            getSupportActionBar().hide();
        }


        findViewById(R.id.speedRow).setOnClickListener(v -> {
            Intent intent = new Intent(this, CursorSpeed.class);
            startActivity(intent);
        });

        findViewById(R.id.bindingRow).setOnClickListener(v -> {
            Intent intent = new Intent(this, CursorBinding.class);
            startActivity(intent);
        });

        findViewById(R.id.bindingRow).setOnClickListener(v -> {
            Intent intent = new Intent(this, CursorBinding.class);
            startActivity(intent);
        });


        findViewById(R.id.helpButton).setOnClickListener(v -> {
            Intent intent = new Intent(this, TutorialActivity.class);
            startActivity(intent);
        });


        Switch gameFaceToggleSwitch = findViewById(R.id.gameFaceToggleSwitch);


        //Check if service is enabled.
        checkIfServiceEnabled();

        // Receive service state message and force toggle the switch accordingly
        BroadcastReceiver toggleStateReceiver = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                Log.i(TAG, "toggleStateReceiver onReceive");
                if (intent.getAction().equals("SERVICE_STATE")) {
                    int stateIndex = intent.getIntExtra("state", CursorAccessibilityService.ServiceState.DISABLE.ordinal());
                    switch (CursorAccessibilityService.ServiceState.values()[stateIndex]) {
                        case ENABLE:
                            gameFaceToggleSwitch.setChecked(true);
                        case PAUSE:
                            gameFaceToggleSwitch.setChecked(true);
                        case GLOBAL_STICK:
                            gameFaceToggleSwitch.setChecked(true);
                            break;
                        case DISABLE:
                            gameFaceToggleSwitch.setChecked(false);
                            break;
                    }

                }
            }

        };
        registerReceiver(toggleStateReceiver, new IntentFilter("SERVICE_STATE"), RECEIVER_EXPORTED);


        // Toggle switch interaction.
        gameFaceToggleSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            if(!checkAccessibilityPermission()){
                gameFaceToggleSwitch.setChecked(false);
                CameraDialog();
            }
            else if(isChecked){
                wakeUpService();
            }
            else {
                sleepCursorService();
            }

        });


        if(isFirstLaunch()){
            // Assign some default binding so user can navigate around.
            Log.i(TAG, "First launch, assign default binding");
            BlendshapeEventTriggerConfig.writeBindingConfig(this, BlendshapeEventTriggerConfig.Blendshape.OPEN_MOUTH,
                    BlendshapeEventTriggerConfig.EventType.CURSOR_TOUCH, 20);
            BlendshapeEventTriggerConfig.writeBindingConfig(this, BlendshapeEventTriggerConfig.Blendshape.MOUTH_LEFT,
                    BlendshapeEventTriggerConfig.EventType.DRAG_TOGGLE, 20);
            BlendshapeEventTriggerConfig.writeBindingConfig(this, BlendshapeEventTriggerConfig.Blendshape.MOUTH_RIGHT,
                    BlendshapeEventTriggerConfig.EventType.CURSOR_RESET, 20);
            preferences.edit().putBoolean(KEY_FIRST_RUN, false).apply();

            // Goto tutorial page.
            Intent intent = new Intent(this, TutorialActivity.class);
            startActivity(intent);




        }

    }



    private void setupUi(){


    }

    /**Send broadcast to service request service enable state
     * Service should send back its state via SERVICE_STATE message*/
    public void checkIfServiceEnabled() {
        // send broadcast to service to check its state.
        Intent intent = new Intent("REQUEST_SERVICE_STATE");
        intent.putExtra("state", "main");
        sendBroadcast(intent);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if(!isFirstLaunch()){
            CameraDialog();
        }

        checkIfServiceEnabled();

    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

    }

    private void CameraDialog() {
        // Check Camera Permission
        if(!checkCameraPermission()){
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            String alertMsg = "Allow Project GameFace to access \nthe camera?";
            builder.setTitle("Access Camera");
            builder.setMessage(alertMsg);
            builder.setPositiveButton("Allow", (dialog, which) -> {
                RequestCameraPermission();
                dialog.dismiss();
            });
            builder.setNegativeButton("Deny", (dialog, which) -> {
                dialog.cancel();
                Intent intent = new Intent(getBaseContext(), GrantPermissionActivity.class);
                intent.putExtra("permission", "grantCamera");
                startActivity(intent);
            });
            AlertDialog alertDialog = builder.create();
            alertDialog.setOnShowListener(dialogInterface -> {
                Button positiveButton = alertDialog.getButton(AlertDialog.BUTTON_POSITIVE);
                positiveButton.setTextColor(getResources().getColor(R.color.blue));
                Button negativeButton = alertDialog.getButton(AlertDialog.BUTTON_NEGATIVE);
                negativeButton.setTextColor(getResources().getColor(R.color.blue));
            });
            alertDialog.setCanceledOnTouchOutside(false);
            alertDialog.show();
            Button positiveButton = alertDialog.getButton(DialogInterface.BUTTON_POSITIVE);
            positiveButton.setTransformationMethod(null);
            Button negativeButton = alertDialog.getButton(DialogInterface.BUTTON_NEGATIVE);
            negativeButton.setTransformationMethod(null);
        } else {
            AccessibilityDialog();
        }
    }

    public void AccessibilityDialog(){
        // Check Accessibility Permission
        if(!checkAccessibilityPermission()){
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            String alertMsg = "Full control is appropriate for apps \nthat help you with accessibility \nneeds, but not for most apps.";
            builder.setTitle("Allow Project GameFace to have full control of your device?");
            builder.setMessage(alertMsg);
            builder.setPositiveButton("Allow", (dialog, which) -> {
                RequestAccessibilityPermission();
                dialog.dismiss();
            });
            builder.setNegativeButton("Deny", (dialog, which) -> {
                dialog.cancel();
                Intent intent = new Intent(getBaseContext(), GrantPermissionActivity.class);
                intent.putExtra("permission", "grantAccessibility");
                startActivity(intent);
            });
            AlertDialog alertDialog = builder.create();
            alertDialog.setOnShowListener(dialogInterface -> {
                Button positiveButton = alertDialog.getButton(AlertDialog.BUTTON_POSITIVE);
                positiveButton.setTextColor(getResources().getColor(R.color.blue));
                Button negativeButton = alertDialog.getButton(AlertDialog.BUTTON_NEGATIVE);
                negativeButton.setTextColor(getResources().getColor(R.color.blue));
            });
            alertDialog.setCanceledOnTouchOutside(false);
            alertDialog.show();
            Button positiveButton = alertDialog.getButton(DialogInterface.BUTTON_POSITIVE);
            positiveButton.setTransformationMethod(null);
            Button negativeButton = alertDialog.getButton(DialogInterface.BUTTON_NEGATIVE);
            negativeButton.setTransformationMethod(null);
        }
    }

    /**
     * Check the local preferences if this is the first time user launch the app.
     * @return boolean flag
     */
    private boolean isFirstLaunch() {
        return preferences.getBoolean(KEY_FIRST_RUN , true);
    }



    public void wakeUpService(){
        Log.i(TAG, "MainActivity wakeUpService");
        findViewById(R.id.gameFaceToggleSwitch).setEnabled(false);
        if (!checkAccessibilityPermission()){
            Log.i(TAG, "MainActivity RequestAccessibilityPermission");
            RequestAccessibilityPermission();
            return;
        }
        if (!checkCameraPermission()){
            Log.i(TAG, "MainActivity RequestCameraPermission");
            RequestCameraPermission();
            return;
        }


        // Run onStartCommand in service, currently doing nothing.
        cursorServiceIntent = new Intent(this, CursorAccessibilityService.class);
        startService(cursorServiceIntent);

        // Send broadcast to wake up service.
        Intent intent = new Intent("CHANGE_SERVICE_STATE");
        intent.putExtra("state", CursorAccessibilityService.ServiceState.ENABLE.ordinal());
        sendBroadcast(intent);

        Intent intentFlyOut = new Intent("FLY_OUT_FLOAT_WINDOW");
        sendBroadcast(intentFlyOut);
        findViewById(R.id.gameFaceToggleSwitch).setEnabled(true);
    }
    public void sleepCursorService(){
        Log.i(TAG, "sleepCursorService");
        findViewById(R.id.gameFaceToggleSwitch).setEnabled(false);
        // Send broadcast to stop service (sleep mode).
        Intent intent = new Intent("CHANGE_SERVICE_STATE");
        intent.putExtra("state", CursorAccessibilityService.ServiceState.DISABLE.ordinal());
        sendBroadcast(intent);
        if (isServiceBound) {
            isServiceBound = false;
        }
        cursorServiceIntent = null;
        findViewById(R.id.gameFaceToggleSwitch).setEnabled(true);

    }

    public boolean checkAccessibilityPermission() {
        int enabled = 0;
        final String gamefaceServiceName = this.getPackageName()
            + "/"
            + this.getPackageName()
            + "."
            + CursorAccessibilityService.class.getSimpleName();

        Log.i(TAG, "GameFace service name: "+gamefaceServiceName);

        try {
            enabled = Settings.Secure.getInt(
                    this.getContentResolver(),
                    Settings.Secure.ACCESSIBILITY_ENABLED
            );
        } catch (Settings.SettingNotFoundException e) {
            // Handle the exception
        }

        TextUtils.SimpleStringSplitter splitter = new TextUtils.SimpleStringSplitter(':');
        if (enabled == 1) {
            String allAccessibilityServices = Settings.Secure.getString(
                    this.getContentResolver(),
                    Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
            );

            if (allAccessibilityServices != null) {
                splitter.setString(allAccessibilityServices);
                while (splitter.hasNext()) {
                    String accessibilityService = splitter.next();
                    if (accessibilityService.equalsIgnoreCase(gamefaceServiceName)) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    // Request accessibility permission using intent
    public void RequestAccessibilityPermission()
    {
        Intent intent = new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }


    public boolean checkCameraPermission()
    {
        return ActivityCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED;
    }


    // Request camera permission using basic requestPermissions method
    public void RequestCameraPermission()
    {

        ActivityCompat.requestPermissions(this, new String[]{
                Manifest.permission.CAMERA
        },CAMERA_PERMISSION_CODE);
    }









}





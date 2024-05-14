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
import android.os.Build.VERSION;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import androidx.activity.OnBackPressedCallback;
import android.view.WindowManager.LayoutParams;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;


/** The cursor binding activity of Gameface app. */
public class CursorBinding extends AppCompatActivity {

    private static final String TAG = "GestureSizeActivity";



    private final int[] viewIds = {
        R.id.tapLayout,
        R.id.homeLayout,
        R.id.backLayout,
        R.id.notificationLayout,
        R.id.allAppLayout,
        R.id.pauseLayout,
        R.id.resetLayout,
        R.id.dragLayout
    };


    TextView textTab;
    TextView tabTxtLinear ;
    TextView textHome;
    TextView homeTxtLinear ;
    TextView textBack;
    TextView backTxtLinear ;
    TextView textNotification ;
    TextView notificationTxtLinear ;
    TextView textAllApp;
    TextView allAppLinear;
    TextView textPause ;
    TextView pauseLinear ;
    TextView textReset;
    TextView resetLinear ;
    TextView textDrag;
    TextView dragLinear;


    protected String getDescriptionTextViewValue() {
        TextView descriptionTextView = findViewById(R.id.tapTxtLinear);
        return descriptionTextView.getText().toString();
    }

    private void setUpActionList(
        String preferencesId,
        TextView textViewAction,
        TextView textViewStatus,
        ImageView statusImage) {
        SharedPreferences preferences = getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);

        // Load config from local sharedpref.
        BlendshapeEventTriggerConfig.Blendshape savedBlendshape = BlendshapeEventTriggerConfig.BLENDSHAPE_FROM_ORDER_IN_UI
            .get(preferences.getInt(preferencesId,
                BlendshapeEventTriggerConfig.BLENDSHAPE_FROM_ORDER_IN_UI.indexOf(
                BlendshapeEventTriggerConfig.Blendshape.NONE)));

        String addTxt = "Add";
        String editTxt = "Edit";
        String beautifyBlendshapeName = BlendshapeEventTriggerConfig.BEAUTIFY_BLENDSHAPE_NAME.get(savedBlendshape);
        textViewAction.setText(beautifyBlendshapeName);



        // Set to "No binding" if not found.
        if (savedBlendshape == BlendshapeEventTriggerConfig.Blendshape.NONE) {
            statusImage.setBackgroundResource(R.drawable.plus);
            textViewStatus.setText(addTxt);
        } else {
            statusImage.setBackgroundResource(R.drawable.outline_edit_24);
            textViewStatus.setText(editTxt);
        }
    }

    private void refreshUI()
    {
        Log.i(TAG, "refreshUI");
        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.CURSOR_TOUCH),
            textTab,
            tabTxtLinear,
            (ImageView) findViewById(R.id.tapIcon));


        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.HOME),
            textHome,
            homeTxtLinear,
            (ImageView) findViewById(R.id.homeIcon));


        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.BACK),
            textBack,
            backTxtLinear,
            (ImageView) findViewById(R.id.backIcon));


        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.SHOW_NOTIFICATION),
            textNotification,
            notificationTxtLinear,
            (ImageView) findViewById(R.id.notificationIcon));


        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.SHOW_APPS),
            textAllApp,
            allAppLinear,
            (ImageView) findViewById(R.id.allAppIcon));
        //Android version < 12 not support ALL_APPS action.
        if (VERSION.SDK_INT < 31) {
            findViewById(R.id.allAppLayout).setVisibility(View.GONE);
        }


        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.CURSOR_PAUSE),
            textPause,
            pauseLinear,
            (ImageView) findViewById(R.id.pauseIcon));


        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.CURSOR_RESET),
            textReset,
            resetLinear,
            (ImageView) findViewById(R.id.resetIcon));


        setUpActionList(
            String.valueOf(BlendshapeEventTriggerConfig.EventType.DRAG_TOGGLE),
            textDrag,
            dragLinear,
            (ImageView) findViewById(R.id.dragIcon));

    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cursor_binding);
        getWindow().addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON);
        // setting actionbar
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        getSupportActionBar().setTitle("Set up gestures");

        textTab = findViewById(R.id.tapBinding);
        tabTxtLinear = findViewById(R.id.tapTxtLinear);
        textHome = findViewById(R.id.homeBinding);
        homeTxtLinear = findViewById(R.id.homeTxtLinear);
        textBack = findViewById(R.id.backBinding);
        backTxtLinear = findViewById(R.id.backTxtLinear);
        textNotification = findViewById(R.id.notificationBinding);
        notificationTxtLinear = findViewById(R.id.notificationTxtLinear);
        textAllApp = findViewById(R.id.allAppBinding);
        allAppLinear = findViewById(R.id.allAppLinear);
        textPause = findViewById(R.id.pauseBinding);
        pauseLinear = findViewById(R.id.pauseLinear);
        textReset = findViewById(R.id.resetBinding);
        resetLinear = findViewById(R.id.resetLinear);
        textDrag = findViewById(R.id.dragBinding);
        dragLinear = findViewById(R.id.dragLinear);

        refreshUI();


        for (int id : viewIds) {
            findViewById(id)
                .setOnClickListener(
                    v -> {

                        // Start intent corresponding to each event action type.
                        Intent intent = new Intent(getBaseContext(),
                            ChooseGestureActivity.class);

                        if (v.getId() == R.id.tapLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.CURSOR_TOUCH);

                        } else if (v.getId() == R.id.homeLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.HOME);

                        } else if (v.getId() == R.id.backLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.BACK);

                        } else if (v.getId() == R.id.notificationLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.SHOW_NOTIFICATION);

                        } else if (v.getId() == R.id.allAppLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.SHOW_APPS);

                        } else if (v.getId() == R.id.pauseLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.CURSOR_PAUSE);

                        } else if (v.getId() == R.id.resetLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.CURSOR_RESET);

                        } else if (v.getId() == R.id.dragLayout) {
                            intent.putExtra("eventType", BlendshapeEventTriggerConfig.EventType.DRAG_TOGGLE);
                        }
                        startActivity(intent);

                    });
        }


        // Make back button work as back action in device's navigation.
        OnBackPressedCallback onBackPressedCallback = new OnBackPressedCallback(true) {
            @Override
            public void handleOnBackPressed() {
                Intent intentHome = new Intent(CursorBinding.this, MainActivity.class);
                startActivity(intentHome);
                finish();
            }
        };
        getOnBackPressedDispatcher().addCallback(this,onBackPressedCallback);

    }


    @Override
    public boolean onOptionsItemSelected(@NonNull MenuItem item) {
      if (item.getItemId() == android.R.id.home) {
        Intent intentHome = new Intent(this, MainActivity.class);
        startActivity(intentHome);
        finish();
        return true;
      }
      return super.onOptionsItemSelected(item);

    }


    @Override
    protected void onResume() {
        refreshUI();
        super.onResume();
    }



}


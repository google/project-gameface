package com.google.projectgameface;

import android.content.Intent;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

public class TutorialPhoneStandActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_tutorial_phone_stand);
        if (getSupportActionBar() != null) {
            getSupportActionBar().hide();
        }

        findViewById(R.id.goHomeButton).setOnClickListener(v -> {

            Intent intent = new Intent(getBaseContext(), MainActivity.class);
            startActivity(intent);
            finish();

        });

        findViewById(R.id.backButton).setOnClickListener(v -> {

            Intent intent = new Intent(getBaseContext(), TutorialActivity.class);
            startActivity(intent);
            finish();

        });

    }
}

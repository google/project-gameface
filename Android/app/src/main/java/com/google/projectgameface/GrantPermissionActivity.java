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

import android.content.Intent;
import android.os.Bundle;
import android.view.WindowManager.LayoutParams;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import java.util.Objects;

public class GrantPermissionActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_grant_permission);
        getWindow().addFlags(LayoutParams.FLAG_KEEP_SCREEN_ON);
        Intent intent = getIntent();
        String permission = intent.getStringExtra("permission"); // Get permission that not been granted.
        TextView description = findViewById(R.id.description);
        ImageView imagePermission = findViewById(R.id.imagePermission);
        if(Objects.equals(permission, "grantAccessibility")){
            description.setText("Change permissions in your device’s \napp settings. Give GameFace access to \nAccessibility.");
            imagePermission.setImageResource(R.drawable.grant_accessibility);
        }
        else if(Objects.equals(permission, "grantCamera")){
            description.setText("Change permissions in your device’s \napp settings. Give GameFace access to \nCamera.");
            imagePermission.setImageResource(R.drawable.grant_camera);
        }
        findViewById(R.id.setting).setOnClickListener(v -> {
            Intent intent1 = new Intent(getBaseContext(), MainActivity.class);
            startActivity(intent1);
        });

        findViewById(R.id.exit).setOnClickListener(v -> finishAffinity());
    }

    protected String getDescriptionTextViewValue() {
        TextView descriptionTextView = findViewById(R.id.description);
        return descriptionTextView.getText().toString();
    }
}
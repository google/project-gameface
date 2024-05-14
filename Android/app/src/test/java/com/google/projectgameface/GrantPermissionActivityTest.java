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

import android.app.Activity;
import android.app.Application;
import android.content.Intent;

import static org.junit.Assert.assertEquals;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import com.google.projectgameface.R;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.Shadows;

@RunWith(AndroidJUnit4.class)
public class GrantPermissionActivityTest {
    private final Activity grantPermissionActivity = Robolectric.buildActivity(GrantPermissionActivity.class).create().get();

    @Test
    public void intent_toMainActivity() {
        grantPermissionActivity.findViewById(R.id.setting).performClick();
        Intent mainActivity = new Intent(grantPermissionActivity, MainActivity.class);
        Intent actual = Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();

        assertEquals(actual.getComponent(), mainActivity.getComponent());
    }

    @Test
    public void intent_toExitApp() {
        grantPermissionActivity.findViewById(R.id.exit).performClick();

        assertEquals(grantPermissionActivity.isFinishing(), true);
    }

    @Test
    public void getIntentValue_getCameraPermissionIndex_returnCameraPermissionMessage() {
        Intent mockIntent = new Intent(ApplicationProvider.getApplicationContext(), GrantPermissionActivity.class);
        mockIntent.putExtra("permission", "grantCamera");

        GrantPermissionActivity grantPermissionActivityResume = Robolectric.buildActivity(GrantPermissionActivity.class, mockIntent).create().start().resume().get();
        String description = grantPermissionActivityResume.getDescriptionTextViewValue();
        String actual = "Change permissions in your device’s \napp settings. Give GameFace access to \nCamera.";

        assertEquals(actual, description);
    }

    @Test
    public void getIntentValue_getAccessibilityPermissionIndex_returnCameraPermissionMessage() {
        Intent mockIntent = new Intent(ApplicationProvider.getApplicationContext(), GrantPermissionActivity.class);
        mockIntent.putExtra("permission", "grantAccessibility");

        GrantPermissionActivity grantPermissionActivityResume = Robolectric.buildActivity(GrantPermissionActivity.class, mockIntent).create().start().resume().get();
        String description = grantPermissionActivityResume.getDescriptionTextViewValue();
        String actual = "Change permissions in your device’s \napp settings. Give GameFace access to \nAccessibility.";

        assertEquals(actual, description);
    }
}

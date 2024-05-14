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

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.Shadows;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class MainActivityTest {

    private final Activity activity = Robolectric.buildActivity(MainActivity.class).create().get();

    @Test
    public void intent_toCursorSpeed() {
        activity.findViewById(R.id.speedRow).performClick();
        Intent cursorSpeedActivity = new Intent(activity, CursorSpeed.class);
        Intent actual = Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();

        assertEquals(actual.getComponent(), cursorSpeedActivity.getComponent());
    }

    @Test
    public void intent_toCursorBinding() {
        activity.findViewById(R.id.bindingRow).performClick();
        Intent CursorBindingActivity = new Intent(activity, CursorBinding.class);
        Intent actual = Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();

        assertEquals(actual.getComponent(), CursorBindingActivity.getComponent());
    }
}
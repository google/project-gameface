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
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;

import com.google.projectgameface.R;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.Shadows;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class ChooseGestureActivityTest {
    private final Activity activityCursorBinding = Robolectric.buildActivity(CursorBinding.class).create().get();

    SharedPreferences preferences = ApplicationProvider.getApplicationContext().getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);

    @Test
    public void selectGesture_chooseToGestureSizeActivity() {
        Activity activityChooseGesture = Robolectric.buildActivity(ChooseGestureActivity.class).create().get();
        activityChooseGesture.findViewById(R.id.rollLowerMouth).performClick();
        activityChooseGesture.findViewById(R.id.nextBtn).performClick();
        Intent gestureSIzeActivity = new Intent(activityChooseGesture, GestureSizeActivity.class);
        Intent actual = Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();

        assertEquals(actual.getComponent(), gestureSIzeActivity.getComponent());
    }

    @Test
    public void checkInUseGesture_mouthRightIsInUes_isNotClickAble() {
        SharedPreferences.Editor editorMock = preferences.edit();
        editorMock.putInt("HOME", 2);
        editorMock.apply();

        activityCursorBinding.findViewById(R.id.tapLayout).performClick();
        Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();
        Activity activityChooseGesture = Robolectric.buildActivity(ChooseGestureActivity.class).create().get();
        boolean isClickable = activityChooseGesture.findViewById(R.id.mouthRight).isClickable();

        assertEquals(isClickable, false);
    }

    @Test
    public void changeGesture_selectNoneGesture_intentToMainActivity() {
        activityCursorBinding.findViewById(R.id.tapLayout).performClick();
        Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();
        Activity activityChooseGesture = Robolectric.buildActivity(ChooseGestureActivity.class).create().get();
        activityChooseGesture.findViewById(R.id.none).performClick();
        activityChooseGesture.findViewById(R.id.nextBtn).performClick();
        Intent actual = Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();
        Intent mainActivity = new Intent(activityChooseGesture, MainActivity.class);

        assertEquals(actual.getComponent(), mainActivity.getComponent());
    }
}

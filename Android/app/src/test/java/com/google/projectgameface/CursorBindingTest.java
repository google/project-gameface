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

import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;
import org.robolectric.Shadows;

import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class CursorBindingTest {
    private final Activity activityCursorBinding = Robolectric.buildActivity(CursorBinding.class).create().get();
    SharedPreferences preferences = ApplicationProvider.getApplicationContext().getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);

    @Test
    public void selectActionBinding_tapToChooseGestureActivity() {
        activityCursorBinding.findViewById(R.id.tapLayout).performClick();
        Intent chooseGestureActivity = new Intent(activityCursorBinding, ChooseGestureActivity.class);
        Intent actual = Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();

        assertEquals(actual.getComponent(), chooseGestureActivity.getComponent());
    }

    @Test
    public void checkActionIsEdit_isNotEdit() {
        SharedPreferences.Editor editorMock = preferences.edit();
        editorMock.putInt("CURSOR_TOUCH", 8);
        editorMock.apply();

        CursorBinding cursorBindingResume = Robolectric.buildActivity(CursorBinding.class).create().start().resume().get();
        String text = cursorBindingResume.getDescriptionTextViewValue();
        String actual = "Add";

        assertEquals(actual, text);
    }

    @Test
    public void checkActionIsEdit_isEdit() {
        SharedPreferences.Editor editorMock = preferences.edit();
        editorMock.putInt("CURSOR_TOUCH", 1);
        editorMock.apply();

        CursorBinding cursorBindingResume = Robolectric.buildActivity(CursorBinding.class).create().start().resume().get();
        String text = cursorBindingResume.getDescriptionTextViewValue();
        String actual = "Edit";

        assertEquals(actual, text);
    }
}

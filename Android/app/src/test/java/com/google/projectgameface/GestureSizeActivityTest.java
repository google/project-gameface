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
import android.widget.SeekBar;

import androidx.test.core.app.ApplicationProvider;
import com.google.projectgameface.R;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.robolectric.Shadows;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class GestureSizeActivityTest {
  private final GestureSizeActivity gestureSizeActivity = new GestureSizeActivity();
  private final Activity activityCursorBinding =
      Robolectric.buildActivity(CursorBinding.class).create().get();

  @Test
  public void tapGestureSize_addGestureSize_returnHigherValueThanDefault() {
    GestureSizeActivity activityGestureSize =
        Robolectric.buildActivity(GestureSizeActivity.class).create().get();
    activityGestureSize.findViewById(R.id.Bigger).performClick();
    SeekBar gestureSizeBar = activityGestureSize.findViewById(R.id.gestureSizeSeekBar);
    int gestureSizeBarValue = gestureSizeBar.getProgress();

    assertEquals(gestureSizeBarValue, gestureSizeActivity.getSeekBarDefaultValue() + 1);
  }

  @Test
  public void tapGestureSize_reduceGestureSize_returnLowerValueThanDefault() {
    GestureSizeActivity activityGestureSize =
        Robolectric.buildActivity(GestureSizeActivity.class).create().get();
    activityGestureSize.findViewById(R.id.Smaller).performClick();
    SeekBar gestureSizeBar = activityGestureSize.findViewById(R.id.gestureSizeSeekBar);
    int gestureSizeBarValue = gestureSizeBar.getProgress();

    assertEquals(gestureSizeBarValue, gestureSizeActivity.getSeekBarDefaultValue() - 1);
  }

  @Test
  public void getIntentValue_enterToGestureSizeActivity_getTouchGestureIndexAndTouchAction() {
    activityCursorBinding.findViewById(R.id.tapLayout).performClick();
    Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();
    Activity activityChooseGesture =
        Robolectric.buildActivity(ChooseGestureActivity.class).create().get();
    activityChooseGesture.findViewById(R.id.rollLowerMouth).performClick();
    activityChooseGesture.findViewById(R.id.nextBtn).performClick();
    Intent actual =
        Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext())
            .getNextStartedActivity();
    int gestureIndex = actual.getIntExtra("selectedGesture", 8);
    String action = actual.getStringExtra("action");

    assertEquals(gestureIndex, 3);
    assertEquals(action, "CURSOR_TOUCH");
  }

  @Test
  public void changeGesture_newGestureAndGestureSize_getGestureSizeIntValue() {
    SharedPreferences preferences =
        ApplicationProvider.getApplicationContext()
            .getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);

    activityCursorBinding.findViewById(R.id.tapLayout).performClick();
    Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext()).getNextStartedActivity();
    Activity activityChooseGesture =
        Robolectric.buildActivity(ChooseGestureActivity.class).create().get();
    activityChooseGesture.findViewById(R.id.rollLowerMouth).performClick();
    activityChooseGesture.findViewById(R.id.nextBtn).performClick();
    Intent intentGestureSize =
        Shadows.shadowOf((Application) ApplicationProvider.getApplicationContext())
            .getNextStartedActivity();
    GestureSizeActivity activityGestureSize =
        Robolectric.buildActivity(GestureSizeActivity.class).create().get();
    activityGestureSize.findViewById(R.id.Bigger).performClick();
    int selectedGesture = intentGestureSize.getIntExtra("selectedGesture", 8);
    String action = intentGestureSize.getStringExtra("action");
    SeekBar gestureSizeBar = activityGestureSize.findViewById(R.id.gestureSizeSeekBar);
    int gestureSizeBarValue = gestureSizeBar.getProgress();
    activityGestureSize.findViewById(R.id.doneBtn).performClick();
    activityGestureSize.saveGestureSelect(
        action, action + "_size", selectedGesture, gestureSizeBarValue * 10);
    int savedTouchGestureSize = preferences.getInt(action + "_size", 0);

    assertEquals(savedTouchGestureSize, 30);
  }
}

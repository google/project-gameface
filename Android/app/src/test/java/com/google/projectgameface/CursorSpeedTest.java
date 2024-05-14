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
import android.view.View;
import android.widget.SeekBar;

import com.google.projectgameface.R;
import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.Robolectric;

import androidx.test.ext.junit.runners.AndroidJUnit4;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class CursorSpeedTest {

    private final Activity activityCursorSpeed = Robolectric.buildActivity(CursorSpeed.class).create().get();

    private static void performButtonClickMultipleTimes(View button, int times) {
        for (int i=0; i < times; i++) {
            button.performClick();
        }
    }

    @Test
    public void changeCursorMovement_increaseValue_returnHigherValueThanDefault() {
        activityCursorSpeed.findViewById(R.id.fasterUp).performClick();
        SeekBar seekBar = activityCursorSpeed.findViewById(R.id.seekBarMU);
        int barValue = seekBar.getProgress();

        Assert.assertEquals(barValue, CursorMovementConfig.InitialRawValue.DEFAULT_SPEED + 1);
    }

    @Test
    public void changeCursorMovement_increaseValueOverMaximum_returnMaximumValue() {
        performButtonClickMultipleTimes(activityCursorSpeed.findViewById(R.id.fasterUp), 10);
        SeekBar seekBar = activityCursorSpeed.findViewById(R.id.seekBarMU);
        int barValue = seekBar.getProgress();

        assertEquals(barValue, CursorSpeed.SEEK_BAR_MAXIMUM_VALUE);
    }

    @Test
    public void changeCursorMovement_decreaseValue_returnLowerValueThanDefault() {
        activityCursorSpeed.findViewById(R.id.slowerUp).performClick();
        SeekBar seekBar = activityCursorSpeed.findViewById(R.id.seekBarMU);
        int barValue = seekBar.getProgress();

        Assert.assertEquals(barValue, CursorMovementConfig.InitialRawValue.DEFAULT_SPEED - 1);
    }

    @Test
    public void changeCursorMovement_decreaseValueOverMinimum_returnMinimumValue() {
        performButtonClickMultipleTimes(activityCursorSpeed.findViewById(R.id.slowerUp), 10);
        SeekBar seekBar = activityCursorSpeed.findViewById(R.id.seekBarMU);
        int barValue = seekBar.getProgress();

        assertEquals(barValue, CursorSpeed.SEEK_BAR_MINIMUM_VALUE);
    }
}

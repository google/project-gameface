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
import android.content.SharedPreferences;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class CursorMovementConfigTest {
  @Test
  public void getConfigSpeed_buildSuccess_returnSpeedValue() {

    CursorMovementConfig testConfig =
        new CursorMovementConfig(ApplicationProvider.getApplicationContext());
    testConfig.setRawValueFromUi(CursorMovementConfig.CursorMovementConfigType.UP_SPEED.toString(), 4);

    // After apply by UI scale (30), up speed should be 120
    Assert.assertEquals(testConfig.get(CursorMovementConfig.CursorMovementConfigType.UP_SPEED), (4 * CursorMovementConfig.RawConfigMultiplier.UP_SPEED), 0.1);

    // Try edit the local preference.
    SharedPreferences preferences =
        ApplicationProvider.getApplicationContext()
            .getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
    SharedPreferences.Editor editor = preferences.edit();
    editor.putInt(CursorMovementConfig.CursorMovementConfigType.UP_SPEED.toString(), 7);
    editor.apply();

    int prefUpSpeed = preferences.getInt(CursorMovementConfig.CursorMovementConfigType.UP_SPEED.toString(), -1);
    assertEquals(prefUpSpeed, 7);

    // Update the value.
    testConfig.updateOneConfigFromSharedPreference(CursorMovementConfig.CursorMovementConfigType.UP_SPEED.toString());
    Assert.assertEquals(testConfig.get(CursorMovementConfig.CursorMovementConfigType.UP_SPEED), (7 * CursorMovementConfig.RawConfigMultiplier.UP_SPEED), 0.1);
  }
}

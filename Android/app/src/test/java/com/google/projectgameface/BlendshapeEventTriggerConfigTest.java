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
public class BlendshapeEventTriggerConfigTest {
  @Test
  public void getOneConfig_buildSuccess_returnBlendshapeAndThreshold() {
    // Create config and set to default.
    BlendshapeEventTriggerConfig testConfig =
        new BlendshapeEventTriggerConfig(ApplicationProvider.getApplicationContext());
    testConfig.updateAllConfigFromSharedPreference();

    // Try edit the local preference.
    SharedPreferences preferences =
        ApplicationProvider.getApplicationContext()
            .getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
    SharedPreferences.Editor editor = preferences.edit();
    // Try set TOUCH-->(RAISE_LEFT_EYEBROW, 0.9)
    // 5 is RAISE_LEFT_EYEBROW.
    editor.putInt(BlendshapeEventTriggerConfig.EventType.CURSOR_TOUCH.toString(), 5);
    // 9 in UI unit will be 0.9 float.
    editor.putInt(BlendshapeEventTriggerConfig.EventType.CURSOR_TOUCH.toString() + "_size", 90);
    editor.apply();

    // Load and apply new config "TOUCH".
    testConfig.updateOneConfigFromSharedPreference(BlendshapeEventTriggerConfig.EventType.CURSOR_TOUCH.toString());

    BlendshapeEventTriggerConfig.BlendshapeAndThreshold shapeAndThreshold =
        testConfig.getAllConfig().get(BlendshapeEventTriggerConfig.EventType.CURSOR_TOUCH);

    Assert.assertEquals(shapeAndThreshold.shape(), BlendshapeEventTriggerConfig.Blendshape.RAISE_LEFT_EYEBROW);
    assertEquals(shapeAndThreshold.threshold(), 0.9f , 0.01);
  }
}

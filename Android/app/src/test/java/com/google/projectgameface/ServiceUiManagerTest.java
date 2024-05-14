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
import android.view.WindowManager;
import androidx.core.content.ContextCompat;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;

import java.util.concurrent.TimeUnit;

import org.junit.Assert;
import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class ServiceUiManagerTest {
  @Test
  public void getOneConfig_buildSuccess_returnBlendshapeAndThreshold() throws InterruptedException {
    Context context = ApplicationProvider.getApplicationContext();
    WindowManager windowManager = ContextCompat.getSystemService(context, WindowManager.class);

    ServiceUiManager testUiServiceManager = new ServiceUiManager(context, windowManager);

    // 1. Camera box should be maximized when first started.
    Assert.assertEquals(testUiServiceManager.cameraBoxState, ServiceUiManager.CameraBoxState.MAXIMIZE);

    // 2. Try minimize camera box.
    testUiServiceManager.minimizeCameraBox();
    Assert.assertEquals(testUiServiceManager.cameraBoxState, ServiceUiManager.CameraBoxState.MINIMIZE);

    // 4. (When camera box is minimized) UI should show pause icon when pause .
    testUiServiceManager.updateStatusIcon(true, false);
    Assert.assertEquals(testUiServiceManager.currentIconState, ServiceUiManager.FloatIconState.PAUSE_ICON);

    // 5. Try resize camera box.
    int newWidth = 123;
    int newHeight = 456;
    testUiServiceManager.resizeCameraBox(newWidth, newHeight);
    TimeUnit.SECONDS.sleep(2);
    assertEquals(testUiServiceManager.cameraBoxLayoutParams.width, newWidth);
    assertEquals(testUiServiceManager.cameraBoxLayoutParams.height, newHeight);
  }
}

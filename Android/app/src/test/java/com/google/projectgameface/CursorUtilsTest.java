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

import android.accessibilityservice.GestureDescription;
import android.graphics.RectF;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.Test;
import org.junit.runner.RunWith;

import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class CursorUtilsTest {
  @Test
  public void createClick_buildSuccess_returnGestureDescription() {

    GestureDescription clickDesscription = CursorUtils.createClick(500.f, 400.f, 0, 100);

    RectF checkBounds = new RectF();
    clickDesscription.getStroke(0).getPath().computeBounds(checkBounds, true);

    assertEquals(checkBounds.left, 500.f, 0.1);
    assertEquals(checkBounds.right, 500.f, 0.1);
    assertEquals(checkBounds.top, 400.f, 0.1);
    assertEquals(checkBounds.bottom, 400.f, 0.1);
  }

  @Test
  public void createSwipe_buildSuccess_returnGestureDescription() {

    GestureDescription swipeDescription = CursorUtils.createSwipe(500.f, 400.f, 50.0f, 50.0f, 100);

    RectF checkBounds = new RectF();
    swipeDescription.getStroke(0).getPath().computeBounds(checkBounds, true);

    assertEquals(checkBounds.left, 500.f, 0.1);
    assertEquals(checkBounds.right, 550.f, 0.1);
    assertEquals(checkBounds.top, 400.f, 0.1);
    assertEquals(checkBounds.bottom, 450.f, 0.1);
  }
}

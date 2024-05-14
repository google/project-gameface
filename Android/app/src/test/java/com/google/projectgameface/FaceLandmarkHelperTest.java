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

import android.graphics.Rect;
import android.media.Image;
import androidx.annotation.Nullable;
import androidx.annotation.NonNull;
import androidx.camera.core.ImageInfo;
import androidx.camera.core.ImageProxy;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.junit.Test;
import org.junit.runner.RunWith;
import static org.junit.Assert.assertEquals;

@RunWith(AndroidJUnit4.class)
public class FaceLandmarkHelperTest {
  @Test
  public void detectLiveStream_buildSuccess_returnForeheadXY() {
    FaceLandmarkerHelper faceLandmarkerHelper = new FaceLandmarkerHelper();

    // Test image proxy.
    ImageProxy imageProxy =
        new ImageProxy() {
          @Override
          public void close() {}

          @NonNull
          @Override
          public Rect getCropRect() {
            return null;
          }

          @Override
          public void setCropRect(@Nullable Rect rect) {}

          @Override
          public int getFormat() {
            return 0;
          }

          @Override
          public int getHeight() {
            return 0;
          }

          @Override
          public int getWidth() {
            return 0;
          }

          @NonNull
          @Override
          public PlaneProxy[] getPlanes() {
            return new PlaneProxy[0];
          }

          @NonNull
          @Override
          public ImageInfo getImageInfo() {
            return null;
          }

          @Nullable
          @Override
          public Image getImage() {
            return null;
          }
        };
    faceLandmarkerHelper.detectLiveStream(imageProxy);

    // Forehead location x, y should be 0.f.
    assertEquals(faceLandmarkerHelper.getHeadCoordXY()[0], 0.f, 0.0001);
    assertEquals(faceLandmarkerHelper.getHeadCoordXY()[1], 0.f, 0.0001);
  }
}

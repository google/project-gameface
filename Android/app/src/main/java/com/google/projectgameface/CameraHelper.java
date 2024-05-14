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
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageAnalysis;
import androidx.camera.core.Preview;
import androidx.camera.core.resolutionselector.AspectRatioStrategy;
import androidx.camera.core.resolutionselector.ResolutionSelector;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.lifecycle.LifecycleOwner;

/** The camera manager of GameFace app. */
public final class CameraHelper {
  static final String TAG = "CameraHelper";
  public static void bindPreview(
      @NonNull ProcessCameraProvider cameraProvider,
      PreviewView previewView,
      ImageAnalysis imageAnalyzer,
      LifecycleOwner lifecycleOwner) {

    cameraProvider.unbindAll();
    Preview preview =
        new Preview.Builder()
            .setResolutionSelector(
                new ResolutionSelector.Builder()
                    .setAspectRatioStrategy(AspectRatioStrategy.RATIO_4_3_FALLBACK_AUTO_STRATEGY)
                    .build())
            .build();


    CameraSelector cameraSelector =
        new CameraSelector.Builder().requireLensFacing(CameraSelector.LENS_FACING_FRONT).build();

    preview.setSurfaceProvider(previewView.getSurfaceProvider());
    cameraProvider.bindToLifecycle(lifecycleOwner, cameraSelector, preview, imageAnalyzer);
  }

  /**
   * Check the orientation of the front camera (usually 270 degrees).
   * @param context Context from main service.
   * @return The orientation degrees of the front camera.
   */
  public static int checkFrontCameraOrientation(Context context) {
    CameraManager cameraManager = (CameraManager) context.getSystemService(Context.CAMERA_SERVICE);

    try {
      String[] cameraList = cameraManager.getCameraIdList();
      for (String availableCameraId : cameraList) {

        CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(availableCameraId);
        boolean isFrontCamera = characteristics.get(CameraCharacteristics.LENS_FACING) == CameraCharacteristics.LENS_FACING_FRONT;

        if (isFrontCamera) {
          int orientation = characteristics.get(CameraCharacteristics.SENSOR_ORIENTATION);
          Log.i(TAG, "checkFrontCameraOrientation: " + orientation);
          return orientation;
        }

      }
    } catch (CameraAccessException e) {
      throw new RuntimeException(e);
    }

    return 0;
  }

  private CameraHelper() {}
}

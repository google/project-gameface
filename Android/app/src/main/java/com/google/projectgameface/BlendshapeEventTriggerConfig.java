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
import android.content.Intent;
import android.content.SharedPreferences;
import android.util.Log;
import androidx.annotation.Nullable;
import com.google.auto.value.AutoValue;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/** The blendshape event trigger config of Gameface app. */
public class BlendshapeEventTriggerConfig {
  private static final String TAG = "BlendshapeEventTriggerConfig";
  private static final int PREFERENCE_INT_NOT_FOUND = -1;

  /** Persistent storage on device (Data/data/{app}) */
  SharedPreferences sharedPreferences;

  /**
   * Events this app can create. such as touch, swipe or some button action. (created event will be
   * dispatch in Accessibility service)
   */
  public enum EventType {
    NONE,
    CURSOR_TOUCH,
    CURSOR_PAUSE,
    CURSOR_RESET,
    SWIPE_LEFT,
    SWIPE_RIGHT,
    SWIPE_UP,
    SWIPE_DOWN,
    DRAG_TOGGLE,
    HOME,
    BACK,
    SHOW_NOTIFICATION,
    SHOW_APPS
  }





  /** Allowed blendshape that our app can use and its array index (from MediaPipe's). */
  public enum Blendshape {
    NONE(-1),
    OPEN_MOUTH(25),
    MOUTH_LEFT(39),
    MOUTH_RIGHT(33),
    ROLL_LOWER_MOUTH(40),
    RAISE_LEFT_EYEBROW(5),
    LOWER_LEFT_EYEBROW(2),
    RAISE_RIGHT_EYEBROW(4),
    LOWER_RIGHT_EYEBROW(1);
    public final int value;

    Blendshape(int index) {
      this.value = index;
    }
  }

  /** For converting blendshapeIndexInUI to Blendshape enum. */
  protected static final List<Blendshape> BLENDSHAPE_FROM_ORDER_IN_UI = Stream.of(
      Blendshape.OPEN_MOUTH, Blendshape.MOUTH_LEFT,
      Blendshape.MOUTH_RIGHT, Blendshape.ROLL_LOWER_MOUTH,
      Blendshape.RAISE_RIGHT_EYEBROW, Blendshape.RAISE_LEFT_EYEBROW,
      Blendshape.LOWER_RIGHT_EYEBROW, Blendshape.LOWER_LEFT_EYEBROW,
      Blendshape.NONE
  ).collect(Collectors.toList());







  @AutoValue
  abstract static class BlendshapeAndThreshold {
    /**
     * Blendshape and its threshold value
     *
     * @param shape The blendshape target {@link Blendshape}.
     * @param threshold The threshold for trigger some gesture.
     * @return Value of blendshape event trigger.
     */
    static BlendshapeAndThreshold create(Blendshape shape, float threshold) {

      return new AutoValue_BlendshapeEventTriggerConfig_BlendshapeAndThreshold(shape, threshold);
    }

    abstract Blendshape shape();

    abstract float threshold();

    /**
     * Create BlendshapeAndThreshold from blendshape order in UI instead of {@link Blendshape}
     *
     * @param blendshapeIndexInUi Index of the blendshape in UI.
     * @param threshold Range 0 - 1.0.
     * @return BlendshapeAndThreshold.
     */
    @Nullable
    public static BlendshapeAndThreshold createFromIndexInUi(
        int blendshapeIndexInUi, float threshold) {
      if ((blendshapeIndexInUi > BLENDSHAPE_FROM_ORDER_IN_UI.size()) || (blendshapeIndexInUi < 0)) {
        Log.w(
            TAG,
            "Cannot create BlendshapeAndThreshold from blendshapeIndexInUi: "
                + blendshapeIndexInUi);
        return null;
      }
      Blendshape shape = BLENDSHAPE_FROM_ORDER_IN_UI.get(blendshapeIndexInUi);
      return BlendshapeAndThreshold.create(shape, threshold);
    }
  }

  private final HashMap<EventType, BlendshapeAndThreshold> configMap;




  /**
   * Stores event and Blendshape pair that will be triggered when the threshold is passed.
   *
   * @param context Context for open SharedPreference in device's local storage.
   */
  public BlendshapeEventTriggerConfig(Context context) {
    Log.i(TAG, "Create BlendshapeEventTriggerConfig.");
    // Create or retrieve SharedPreference.
    sharedPreferences = context.getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);

    configMap = new HashMap<>();

    updateAllConfigFromSharedPreference();
  }

  /** Get every EventType-BlendshapeAndThreshold pairs. */
  public HashMap<EventType, BlendshapeAndThreshold> getAllConfig() {
    return configMap;
  }

  public void updateAllConfigFromSharedPreference() {
    Log.i(TAG, "Update all config from local SharedPreference...");
    for (EventType eventType : EventType.values()) {
      updateOneConfigFromSharedPreference(eventType.name());
    }
  }

  /**
   * Update the face blendshape event trigger config from SharedPreference.
   *
   * @param eventTypeString String of {@link EventType} to update, such as "TOUCH" or "SWIPE_LEFT".
   */
  public void updateOneConfigFromSharedPreference(String eventTypeString) {
    Log.i(TAG, "updateOneConfigFromSharedPreference: " + eventTypeString);

    if (sharedPreferences == null) {
      Log.w(TAG, "sharedPreferences instance does not exist.");
      return;
    }

    EventType eventType;
    try {
      eventType = EventType.valueOf(eventTypeString);
    } catch (IllegalArgumentException e) {
      Log.w(TAG, eventTypeString + " not exist in EventType enum.");
      return;
    }

    int blendshapeIndexInUi = sharedPreferences.getInt(eventTypeString, -1);
    if (blendshapeIndexInUi == -1) {
      Log.i(
          TAG,
          "Key " + eventTypeString + " not found in SharedPreference, keep using default value.");
      return;
    }

    int thresholdInUi =
        sharedPreferences.getInt(eventTypeString + "_size", PREFERENCE_INT_NOT_FOUND);
    if (thresholdInUi == PREFERENCE_INT_NOT_FOUND) {
      Log.w(TAG, "Cannot find " + eventTypeString + "_size" + " in SharedPreference.");
      return;
    }

    float threshold = (float) thresholdInUi / 100.f;
    BlendshapeAndThreshold blendshapeAndThreshold =
        BlendshapeAndThreshold.createFromIndexInUi(blendshapeIndexInUi, threshold);

    if (blendshapeAndThreshold != null) {
      configMap.put(eventType, blendshapeAndThreshold);
      Log.i(
          TAG,
          "Apply "
              + eventType.name()
              + " with value: "
              + blendshapeAndThreshold.shape()
              + " "
              + blendshapeAndThreshold.threshold());
    }
  }


  /**
   * Write binding config to local sharedpref a
   * nd also send broadcast to tell background service to update its config.
   * @param blendshape What face gesture needed to perform.
   * @param eventType What event action to trigger.
   * @param thresholdInUI threshold in UI unit from 0 to 100.
   */
  static void writeBindingConfig(Context context, Blendshape blendshape, EventType eventType,
      int thresholdInUI)
  {
    Log.i(TAG, "writeBindingConfig: " + blendshape.toString() +" "+ eventType.toString() + " " + thresholdInUI);

    SharedPreferences preferences = context.getSharedPreferences("GameFaceLocalConfig", Context.MODE_PRIVATE);
    SharedPreferences.Editor editor = preferences.edit();
    editor.putInt(eventType.toString(), BLENDSHAPE_FROM_ORDER_IN_UI.indexOf(blendshape));
    editor.putInt(eventType.toString()+"_size", thresholdInUI);
    editor.apply();

    // Tell service to refresh its config.
    Intent intent = new Intent("LOAD_SHARED_CONFIG_GESTURE");
    intent.putExtra("configName", eventType.toString());
    context.sendBroadcast(intent);
  }

  /**
   * Get UI text of event string name.
   * @param eventType
   */
  public static String getActionName(Context context, EventType eventType) {
    String[] keys = context.getResources().getStringArray(R.array.event_type_keys);
    String[] values = context.getResources().getStringArray(R.array.event_type_keys_values);

    int index = Arrays.asList(keys).indexOf(String.valueOf(eventType));
    return values[index];
  }

  /**
   * Get description text of event action type.
   * @param eventType
   * @return
   */
  public static String getActionDescription(Context context, BlendshapeEventTriggerConfig.EventType eventType) {


    String[] keys = context.getResources().getStringArray(R.array.event_type_description_keys);
    String[] values = context.getResources().getStringArray(R.array.event_type_description_keys_values);

    int index = Arrays.asList(keys).indexOf(String.valueOf(eventType));
    return values[index];

  }

  /**
   * Get UI text of blendshape name.
   * @param blendshape
   */
  public static String getBlendshapeName(Context context, BlendshapeEventTriggerConfig.Blendshape blendshape) {


    String[] keys = context.getResources().getStringArray(R.array.blendshape_keys);
    String[] values = context.getResources().getStringArray(R.array.blendshape_keys_values);

    int index = Arrays.asList(keys).indexOf(String.valueOf(blendshape));
    return values[index];
  }


}
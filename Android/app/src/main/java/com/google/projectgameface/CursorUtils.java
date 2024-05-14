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

import static androidx.core.math.MathUtils.clamp;
import static java.lang.Math.max;

import android.accessibilityservice.GestureDescription;
import android.graphics.Path;

/** The Utils of cursor. */
public final class CursorUtils {
    private static final String TAG = "CursorUtils";

    /**
     * Create GestureDes
     *
     * @param x The x-coordinate
     * @param y The y-coordinate
     * @param start The time, in milliseconds, from the time the gesture starts to the time the
     *     stroke should start. Must not be negative.
     * @param duration The duration, in milliseconds, the stroke takes to traverse the path. Must be
     *     positive.
     * @return Result description for dispatching.
     */
    public static GestureDescription createClick(float x, float y, long start, long duration) {
        // for a single tap a duration of 1 ms is enough

        Path clickPath = new Path();
        clickPath.moveTo(clamp(x, 0, Float.MAX_VALUE), clamp(y, 0, Float.MAX_VALUE));
        GestureDescription.StrokeDescription clickStroke =
            new GestureDescription.StrokeDescription(clickPath, start, max(duration, 1));
        GestureDescription.Builder clickBuilder = new GestureDescription.Builder();
        clickBuilder.addStroke(clickStroke);
        return clickBuilder.build();
    }

    /**
     * Create swipe action. Since accessibility service cannot create real-time drag action we use
     * this to imitate drag by execute the swipe with pre defined path.
     *
     * @param x The x-coordinate
     * @param y The y-coordinate
     * @param xOffset The traverse distance in x axis.
     * @param yOffset The traverse distance in y axis.
     * @param duration The duration, in milliseconds, the stroke takes to traverse the path. Must be
     *     positive.
     * @return Result description for dispatching.
     */
    public static GestureDescription createSwipe(
        float x, float y, float xOffset, float yOffset, int duration) {
        // for a single tap a duration of 1 ms is enough
        Path path = new Path();

        path.moveTo(clamp(x, 0, Float.MAX_VALUE), clamp(y, 0, Float.MAX_VALUE));
        path.lineTo(clamp(x + xOffset, 0, Float.MAX_VALUE), clamp(y + yOffset, 0, Float.MAX_VALUE));

        GestureDescription.Builder clickBuilder = new GestureDescription.Builder();
        clickBuilder.addStroke(new GestureDescription.StrokeDescription(path, 0, max(duration, 1)));
        return clickBuilder.build();
    }

    private CursorUtils() {}
}

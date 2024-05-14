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
import android.graphics.Canvas;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;
import androidx.core.content.ContextCompat;

/** The camera overlay of camera feed. */
public class CameraBoxOverlay extends View {

    private static final int DEBUG_TEXT_LOC_X = 10;
    private static final int DEBUG_TEXT_LOC_Y = 250;

    /** White dot on user head. */
    private float whiteDotX = -100.f;

    private float whiteDotY = -100.f;

    private String preprocessTimeText = "";
    private String mediapipeTimeText = "";
    private String pauseIndicatorText = "";

    private Paint paint;

    public CameraBoxOverlay(Context context, AttributeSet attributeSet) {
        super(context, attributeSet);
        paint = new Paint();
        paint.setStyle(Paint.Style.FILL);
        paint.setColor(ContextCompat.getColor(getContext(), android.R.color.white));
        paint.setTextSize(32);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        canvas.drawCircle(whiteDotX, whiteDotY, 5, paint);
        canvas.drawText(preprocessTimeText, DEBUG_TEXT_LOC_X, DEBUG_TEXT_LOC_Y, paint);
        canvas.drawText(mediapipeTimeText, DEBUG_TEXT_LOC_X, DEBUG_TEXT_LOC_Y + 50, paint);
        canvas.drawText(pauseIndicatorText, DEBUG_TEXT_LOC_X, DEBUG_TEXT_LOC_Y + 100, paint);
    }

    public void setWhiteDot(float x, float y) {
        whiteDotX = x;
        whiteDotY = y;
        invalidate();
    }

    public void setOverlayInfo(long preprocessValue, long mediapipeValue) {
        preprocessTimeText = "pre: " + preprocessValue + " ms";
        mediapipeTimeText = "med: " + mediapipeValue + " ms";
        invalidate();
    }

    public void setPauseIndicator(boolean isPause) {
        if (isPause) {
            preprocessTimeText = "";
            mediapipeTimeText = "";
            pauseIndicatorText = "pause";
        } else {
            pauseIndicatorText = "";
        }
    }
}
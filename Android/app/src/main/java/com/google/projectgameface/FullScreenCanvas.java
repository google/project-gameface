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
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

/** The drag cursor of cursor service. */
public class FullScreenCanvas extends View {

    private int holdRadius = 75;
    private float drawX = 500.f;
    private float drawY = 500.f;

    private final Paint touchCirclePaint;
    private final Paint dragLinePaint;
    private final Paint holdCirclePaint;

    private boolean isShowingDrag = false;
    private float dragStartX = 0;
    private float dragStartY = 0;
    private float dragEndX = 0;
    private float dragEndY = 0;


    private boolean isShowingTouch = false;

    public FullScreenCanvas(Context context, AttributeSet attributeSet) {
        super(context, attributeSet);
        touchCirclePaint = new Paint();
        touchCirclePaint.setStyle(Paint.Style.FILL);
        touchCirclePaint.setColor(Color.parseColor("#04DE71"));

        dragLinePaint = new Paint();
        dragLinePaint.setStrokeWidth(15);
        dragLinePaint.setColor(Color.parseColor("#04DE71"));

        holdCirclePaint = new Paint();
        holdCirclePaint.setStyle(Paint.Style.STROKE);
        holdCirclePaint.setColor(Color.parseColor("#4285f4"));
        holdCirclePaint.setStrokeWidth(10);
    }


    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);

        if (isShowingTouch) {
            canvas.drawCircle(drawX, drawY, 25, touchCirclePaint);
            isShowingTouch = false;
            postInvalidateDelayed(30);
        }
        if (isShowingDrag) {
            canvas.drawLine(dragStartX, dragStartY, dragEndX, dragEndY, dragLinePaint);
            canvas.drawCircle(dragStartX, dragStartY, holdRadius, holdCirclePaint);
        }
    }

    public void drawTouchCircle(float x, float y) {
        drawX = x;
        drawY = y;

        invalidate();
        isShowingTouch = true;
    }

    public void setDragLineStart(float x, float y) {
        dragStartX = x;
        dragStartY = y;
        isShowingDrag = true;
    }

    public void updateDragLine(float x, float y) {
        dragEndX = x ;
        dragEndY = y ;

        invalidate();
    }

    public void clearDragLine() {
        isShowingDrag = false;
        invalidate();
    }


    /**
     * Set draw radius size for hold action.
     * @param holdRadius
     */
    public void setHoldRadius(float holdRadius) {
        this.holdRadius = (int) holdRadius;
    }
}
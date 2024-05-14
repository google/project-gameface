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

import android.content.Context;
import android.util.Log;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

public class CursorController {

    private static final String TAG = "CursorController";


    /** How much you need to move the head to trigger teleport */
    private static final int TELEPORT_TRIGGER_THRESHOLD = 200;

    private static final int TELEPORT_MARGIN_TOP = 60;
    private static final int TELEPORT_MARGIN_BOTTOM = 60;

    private static final int TELEPORT_MARGIN_LEFT = 30;
    private static final int TELEPORT_MARGIN_RIGHT = 30;

    /** How fast cursor can go in teleport mode*/
    private static final double TELEPORT_LERP_SPEED = 0.15;


    // Cursor velocity.
    private float velX = 0.f;
    private float velY = 0.f;

    /** Cursor position.*/
    private double cursorPositionX;

    /** Cursor position.*/
    private double cursorPositionY;


    /** Invisible cursor when using teleport mode.*/
    private double teleportShadowX;
    private double teleportShadowY;

    /** Teleport mode helps user quickly jump to screen edge with small head turning.*/
    private boolean isTeleportMode = false;

    public boolean isDragging = false;

    private static final int MAX_BUFFER_SIZE = 100;

    /** Array for storing user face coordinate x coordinate (detected from FaceLandmarks). */
    ArrayList<Float> faceCoordXBuffer;

    /** Array for storing user face coordinate y coordinate (detected from FaceLandmarks). */
    ArrayList<Float> faceCoordYBuffer;

    private float prevX = 0.f;
    private float prevY = 0.f;
    private float prevSmallStepX = 0.0f;
    private float prevSmallStepY = 0.0f;

    public float dragStartX = 0.f;
    public float dragStartY = 0.f;
    public float dragEndX = 0.f;
    public float dragEndY = 0.f;

    private int screenWidth = 0;
    private int screenHeight = 0;

    public CursorMovementConfig cursorMovementConfig;

    /** A Config define which face shape should trigger which event */
    BlendshapeEventTriggerConfig blendshapeEventTriggerConfig;

    /** Keep tracking if any event is triggered. */
    private final HashMap<BlendshapeEventTriggerConfig.EventType, Boolean> blendshapeEventTriggeredTracker = new HashMap<>();

    /**
     * Calculate cursor movement and keeping track of face action events.
     *
     * @param context Context for open SharedPreference
     */
    public CursorController(Context context) {
        faceCoordXBuffer = new ArrayList<>();
        faceCoordYBuffer = new ArrayList<>();

        // Create cursor movement config and initialize;
        cursorMovementConfig = new CursorMovementConfig(context);
        cursorMovementConfig.updateAllConfigFromSharedPreference();

        // Create blendshape event trigger config and initialize;
        blendshapeEventTriggerConfig = new BlendshapeEventTriggerConfig(context);
        blendshapeEventTriggerConfig.updateAllConfigFromSharedPreference();

        // Init blendshape event tracker.
        for (BlendshapeEventTriggerConfig.EventType eventType : BlendshapeEventTriggerConfig.EventType.values()) {
            blendshapeEventTriggeredTracker.put(eventType, false);
        }
    }

    /** Scale cursor velocity X, Y with different multiplier in each axis. */
    private float[] asymmetryScaleXy(float velX, float velY) {
        // Speed multiplier in X axis.
        float multiplierX =
            (velX > 0)
                ? cursorMovementConfig.get(CursorMovementConfig.CursorMovementConfigType.RIGHT_SPEED)
                : cursorMovementConfig.get(CursorMovementConfig.CursorMovementConfigType.LEFT_SPEED);

        // Speed multiplier in Y axis.
        float multiplierY =
            (velY > 0)
                ? cursorMovementConfig.get(CursorMovementConfig.CursorMovementConfigType.DOWN_SPEED)
                : cursorMovementConfig.get(CursorMovementConfig.CursorMovementConfigType.UP_SPEED);

        return new float[] {velX * multiplierX, velY * multiplierY};
    }

    /**
     * Calculate cursor velocity from face coordinate location. Use getVelX() and get getVelY() to
     * receive it.
     */
    private void updateVelocity(float[] faceCoordXy) {
        float faceCoordX = faceCoordXy[0];
        float faceCoordY = faceCoordXy[1];

        faceCoordXBuffer.add(faceCoordX);
        faceCoordYBuffer.add(faceCoordY);

        // Calculate speed
        float tempVelX = faceCoordX - prevX;
        float tempVelY = faceCoordY - prevY;

        float[] result = asymmetryScaleXy(tempVelX, tempVelY);

        this.velX = result[0];
        this.velY = result[1];

        // History
        prevX = faceCoordX;
        prevY = faceCoordY;

        if (faceCoordXBuffer.size() > MAX_BUFFER_SIZE) {
            faceCoordXBuffer.remove(0);
            faceCoordYBuffer.remove(0);
        }
    }

    /**
     * Create performable event from blendshapes array if its threshold value reach the threshold.
     *
     * @param blendshapes The blendshapes array from MediaPipe FaceLandmarks model.
     * @return EventType that should be trigger. Will be {@link BlendshapeEventTriggerConfig.EventType#NONE} if no valid event.
     */
    public BlendshapeEventTriggerConfig.EventType createCursorEvent(float[] blendshapes) {
        // Loop over registered event-blendshape-threshold pairs.
        for (Map.Entry<BlendshapeEventTriggerConfig.EventType, BlendshapeEventTriggerConfig.BlendshapeAndThreshold> entry :
            blendshapeEventTriggerConfig.getAllConfig().entrySet()) {
            BlendshapeEventTriggerConfig.EventType eventType = entry.getKey();
            BlendshapeEventTriggerConfig.BlendshapeAndThreshold blendshapeAndThreshold = entry.getValue();

            if (blendshapeAndThreshold.shape() == BlendshapeEventTriggerConfig.Blendshape.NONE) {
                continue;
            }
            if (blendshapeEventTriggeredTracker.get(eventType) == null) {
                continue;
            }
            float score = blendshapes[blendshapeAndThreshold.shape().value];

            boolean eventTriggered = Boolean.TRUE.equals(blendshapeEventTriggeredTracker.get(eventType));

            if (!eventTriggered && (score > blendshapeAndThreshold.threshold())) {
                blendshapeEventTriggeredTracker.put(eventType, true);
                if (eventType == BlendshapeEventTriggerConfig.EventType.SHOW_APPS) {
                    Log.i(
                        TAG,
                        eventType
                            + " "
                            + blendshapeAndThreshold.shape()
                            + " "
                            + score
                            + " "
                            + blendshapeAndThreshold.threshold());
                }

                // Return the correspond event (te be trigger in Accessibility service).

                if (eventType == BlendshapeEventTriggerConfig.EventType.CURSOR_RESET)
                {
                    isTeleportMode = true;
                    teleportShadowX = (double) this.screenWidth / 2;
                    teleportShadowY = (double) this.screenHeight / 2;
                }

                return eventType;

            } else if (eventTriggered && (score <= blendshapeAndThreshold.threshold())) {
                // Reset the trigger.
                blendshapeEventTriggeredTracker.put(eventType, false);
                if (eventType == BlendshapeEventTriggerConfig.EventType.CURSOR_RESET)
                {
                    isTeleportMode=false;
                }

            } else {
                // check next gesture.
                continue;
            }
        }

        // No action.
        return BlendshapeEventTriggerConfig.EventType.NONE;
    }

    /**
     * Calculate cursor's translation XY and smoothing.
     *
     * @param faceCoordXy User head coordinate x,y from FaceLandmarks tracker.
     * @param gapFrames How many screen frame with no update from FaceLandmarks. Used when calculate
     *     smoothing.
     */
    public float[] getCursorTranslateXY(float[] faceCoordXy, int gapFrames) {
        this.updateVelocity(faceCoordXy);
        int smooth = (int) cursorMovementConfig.get(CursorMovementConfig.CursorMovementConfigType.SMOOTH_POINTER);

        float smallStepX = (smooth * prevSmallStepX + velX / (float) gapFrames) / (smooth + 1);
        float smallStepY = (smooth * prevSmallStepY + velY / (float) gapFrames) / (smooth + 1);

        prevSmallStepX = smallStepX;
        prevSmallStepY = smallStepY;

        return new float[] {smallStepX, smallStepY};
    }

    /**
     * Set start point for drag action.
     *
     * @param x coordinate x of cursor.
     * @param y coordinate y of cursor.
     */
    public void prepareDragStart(float x, float y) {
        dragStartX = x;
        dragStartY = y;
        isDragging = true;
    }

    /**
     * Set end point for drag action.
     *
     * @param x coordinate x of cursor.
     * @param y coordinate y of cursor.
     */
    public void prepareDragEnd(float x, float y) {
        dragEndX = x;
        dragEndY = y;
        isDragging = false;
    }



    private double[] getTeleportLocation()
    {
        double teleportDegrees;
        double screenCenterX = (double) this.screenWidth / 2;
        double screenCenterY = (double) this.screenHeight /2;

        double distanceFromCenter = euclideanDistance(
            screenCenterX,
            screenCenterY,
            teleportShadowX,
            teleportShadowY);

        // Reject, go to screen center.
        if (distanceFromCenter < TELEPORT_TRIGGER_THRESHOLD)
        {
            return new double[]{screenCenterX, screenCenterY};
        }

        // Calculate teleport location.
        double angle1 = Math.atan2(0, 1);
        double angle2 = Math.atan2(
            teleportShadowY - screenCenterY,
            teleportShadowX - screenCenterX
        );

        teleportDegrees =  Math.toDegrees(angle1 - angle2);

        teleportDegrees = (teleportDegrees + 360) % 360;
        double segmentSize = 360.0 / 8;
        int segmentIndex = (int) Math.floor((teleportDegrees + segmentSize / 2 )/ segmentSize);


        // Teleport edges.
        int edgeMinX = TELEPORT_MARGIN_LEFT;
        int edgeCenterX = (int) screenCenterX;
        int edgeMaxX = this.screenWidth - TELEPORT_MARGIN_RIGHT;

        int edgeMinY = TELEPORT_MARGIN_TOP;
        int edgeCenterY = (int) screenCenterY;
        int edgeMaxY = this.screenHeight - TELEPORT_MARGIN_BOTTOM;

        switch (segmentIndex){
            case 0:
            case 8:
                // East.
                return new double[]{edgeMaxX, edgeCenterY};

            case 7:
                // South-East.
                return new double[]{edgeMaxX, edgeMaxY};
            case 1:
                // North-East.
                return new double[]{edgeMaxX, edgeMinY};
            case 2:
                // North.
                return new double[]{edgeCenterX, edgeMinY};
            case 3:
                // North-West.
                return new double[]{edgeMinX, edgeMinY};
            case 4:
                // West.
                return new double[]{edgeMinX, edgeCenterY};
            case 5:
                // South-West.
                return new double[]{edgeMinX, edgeMaxY};
            case 6:
                // South.
                return new double[]{edgeCenterX, edgeMaxY};
            default:
                // Should never be reached.
                return new double[]{edgeCenterX,edgeCenterY};

        }
    }


    private static double euclideanDistance(double vecAX, double vecAY, double vecBX, double vecBY)
    {
        double dx = vecBX - vecAX;
        double dy = vecBY - vecAY;

        double dxSquared = dx * dx;
        double dySquared = dy * dy;

        return Math.sqrt(dxSquared + dySquared);
    }


    /**
     * Update internal cursor position.
     * @param headCoordXY User head coordinate.
     * @param gapFrames How many frames we use to wait for the FaceLandmarks model.
     * @param screenWidth Screen size for prevent cursor move out of of the screen.
     * @param screenHeight Screen size for prevent cursor move out of of the screen.
     */
    public void updateInternalCursorPosition(float[] headCoordXY,int gapFrames,
        int screenWidth, int screenHeight
    ){

        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;

        // How far we should move this frame.
        float[] offsetXY =  this.getCursorTranslateXY(
            headCoordXY,
            gapFrames);


        // In teleport mode, apply offset to shadow cursor
        // but teleport the real cursor.
        if (isTeleportMode) {
            teleportShadowX += offsetXY[0];
            teleportShadowY += offsetXY[1];

            // Clamp x, y to screen.
            teleportShadowX = clamp(teleportShadowX, 0, screenWidth);
            teleportShadowY = clamp(teleportShadowY, 0, screenHeight);

            double[] teleportLocation = getTeleportLocation();
            cursorPositionX = cursorPositionX * (1 - TELEPORT_LERP_SPEED) + teleportLocation[0] * TELEPORT_LERP_SPEED;
            cursorPositionY = cursorPositionY * (1 - TELEPORT_LERP_SPEED) + teleportLocation[1] * TELEPORT_LERP_SPEED;

            return;
        }

        cursorPositionX += offsetXY[0];
        cursorPositionY += offsetXY[1];

        // Clamp x, y to screen.
        cursorPositionX =
            clamp(cursorPositionX,
                0,
                screenWidth);

        cursorPositionY =
            clamp(
                cursorPositionY,
                0,
                screenHeight);

    }



    public int[] getCursorPositionXY()
    {

        return new int[]{(int) cursorPositionX, (int)cursorPositionY};
    }


    public void resetCursorToCenter()
    {
        cursorPositionX = (double) this.screenWidth / 2;
        cursorPositionY = (double) this.screenHeight / 2;

    }


}

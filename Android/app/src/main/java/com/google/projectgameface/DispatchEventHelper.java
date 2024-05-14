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


import android.accessibilityservice.AccessibilityService;


public class DispatchEventHelper {
  /** Duration for swipe action. Should be fast enough to change page in launcher app. */
  private static final int SWIPE_DURATION_MS = 100;
  private static final int DRAG_DURATION_MS = 250;

  /**
   * Helper function to check the event type and dispatch the events desired location.
   * @param parentService Need for calling {@link AccessibilityService#dispatchGesture}.
   * @param cursorController Some event need cursor control.
   * @param serviceUiManager For drawing drag line on canvas.
   * @param event Event to dispatch.
   */
  public static void checkAndDispatchEvent(
      CursorAccessibilityService parentService,
      CursorController cursorController,
      ServiceUiManager serviceUiManager,
      BlendshapeEventTriggerConfig.EventType event) {


    int[] cursorPosition = cursorController.getCursorPositionXY();

    int  eventOffsetX = 0;
    int eventOffsetY =0;


    switch (event) {
      case CURSOR_TOUCH:
        parentService.dispatchGesture(
            CursorUtils.createClick(
                cursorPosition[0] ,
                cursorPosition[1] ,
                /* startTime= */ 0,
                /* duration= */ 250),
            /* callback= */ null,
            /* handler= */ null);

        serviceUiManager.drawTouchDot(cursorController.getCursorPositionXY());
        break;

      case CURSOR_PAUSE:
        parentService.togglePause();
        break;

      case CURSOR_RESET:
        cursorController.resetCursorToCenter();
        break;

      case SWIPE_LEFT:
        parentService.dispatchGesture(
            CursorUtils.createSwipe(
                cursorPosition[0] + eventOffsetX,
                cursorPosition[1] + eventOffsetY,
                /* xOffset= */ -500,
                /* yOffset= */ 0,
                /* duration= */ SWIPE_DURATION_MS),
            /* callback= */ null,
            /* handler= */ null);
        break;

      case SWIPE_RIGHT:
        parentService.dispatchGesture(
            CursorUtils.createSwipe(
                cursorPosition[0] + eventOffsetX,
                cursorPosition[1] + eventOffsetY,
                /* xOffset= */ 500,
                /* yOffset= */ 0,
                /* duration= */ SWIPE_DURATION_MS),
            /* callback= */ null,
            /* handler= */ null);
        break;

      case SWIPE_UP:
        parentService.dispatchGesture(
            CursorUtils.createSwipe(
                cursorPosition[0] + eventOffsetX,
                cursorPosition[1] + eventOffsetY,
                /* xOffset= */ 0,
                /* yOffset= */ -500,
                /* duration= */ SWIPE_DURATION_MS),
            /* callback= */ null,
            /* handler= */ null);
        break;

      case SWIPE_DOWN:
        parentService.dispatchGesture(
            CursorUtils.createSwipe(
                cursorPosition[0] + eventOffsetX,
                cursorPosition[1] + eventOffsetY,
                /* xOffset= */ 0,
                /* yOffset= */ 500,
                /* duration= */ SWIPE_DURATION_MS),
            /* callback= */ null,
            /* handler= */ null);
        break;

      case DRAG_TOGGLE:
        dispatchDragOrHold(parentService, cursorController, serviceUiManager,
            eventOffsetX, eventOffsetY);
        break;

      case HOME:
        parentService.performGlobalAction(AccessibilityService.GLOBAL_ACTION_HOME);
        break;

      case BACK:
        parentService.performGlobalAction(AccessibilityService.GLOBAL_ACTION_BACK);
        break;

      case SHOW_NOTIFICATION:
        parentService.performGlobalAction(AccessibilityService.GLOBAL_ACTION_NOTIFICATIONS);
        break;

      case SHOW_APPS:
        parentService.performGlobalAction(AccessibilityService.GLOBAL_ACTION_ACCESSIBILITY_ALL_APPS);
        break;
      default:
    }
  }

  private static void dispatchDragOrHold(
      CursorAccessibilityService parentService,
      CursorController cursorController,
      ServiceUiManager serviceUiManager,
      int eventOffsetX, int eventOffsetY) {

    int[] cursorPosition = cursorController.getCursorPositionXY();

    // Register new drag action.
    if (!cursorController.isDragging) {

      cursorController.prepareDragStart(
          cursorPosition[0] + eventOffsetX,
          cursorPosition[1] + eventOffsetY);

      serviceUiManager.fullScreenCanvas.setHoldRadius(
          cursorController.cursorMovementConfig.get(CursorMovementConfig.CursorMovementConfigType.HOLD_RADIUS));

      serviceUiManager.setDragLineStart(
          cursorPosition[0], cursorPosition[1]);

    }
    // Finish drag action.
    else {
      cursorController.prepareDragEnd(
          cursorPosition[0] + eventOffsetX,
          cursorPosition[1] + eventOffsetY);
      serviceUiManager.fullScreenCanvas.clearDragLine();

      // Cursor path distance.
      float xOffset = cursorController.dragEndX - cursorController.dragStartX;
      float yOffset = cursorController.dragEndY - cursorController.dragStartY;

      // Is action finished inside defined circle or not.
      boolean isFinishedInside =
          (Math.abs(xOffset)
              < cursorController.cursorMovementConfig.get(CursorMovementConfig.CursorMovementConfigType.HOLD_RADIUS))
              && (Math.abs(yOffset)
              < cursorController.cursorMovementConfig.get(
              CursorMovementConfig.CursorMovementConfigType.HOLD_RADIUS));

      // If finished inside a circle, trigger HOLD action.
      if (isFinishedInside) {
        // Dispatch HOLD event.
        parentService.dispatchGesture(
            CursorUtils.createClick(
                cursorController.dragStartX,
                cursorController.dragStartY,
                0,
                (long)
                    cursorController.cursorMovementConfig.get(
                        CursorMovementConfig.CursorMovementConfigType.HOLD_TIME_MS)),
            /* callback= */ null,
            /* handler= */ null);

      }
      // Trigger normal DRAG action.
      else {
        parentService.dispatchGesture(
            CursorUtils.createSwipe(
                cursorController.dragStartX,
                cursorController.dragStartY,
                xOffset,
                yOffset,
                /* duration= */ DRAG_DURATION_MS),
            /* callback= */ null,
            /* handler= */ null);
      }
    }
  }
}

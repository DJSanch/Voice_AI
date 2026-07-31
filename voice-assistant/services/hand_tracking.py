import cv2
import mediapipe as mp
import time


class HandTrackingService:


    def __init__(self):

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7
        )

        self.hand_detected_time = None



    def close_camera(self, camera):

        camera.release()

        cv2.destroyAllWindows()

        # Allow macOS OpenCV window to process close event
        for _ in range(5):
            cv2.waitKey(1)



    def capture_hand_region(self):

        camera = cv2.VideoCapture(0)

        captured_image = None
        crop = None


        while True:


            success, frame = camera.read()


            if not success:
                continue



            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )


            results = self.hands.process(rgb)



            if results.multi_hand_landmarks:


                hand = results.multi_hand_landmarks[0]


                height, width, _ = frame.shape


                xs = []
                ys = []


                for landmark in hand.landmark:

                    xs.append(
                        int(
                            landmark.x * width
                        )
                    )

                    ys.append(
                        int(
                            landmark.y * height
                        )
                    )



                padding_x = 100
                padding_y = 100


                x1 = max(
                    min(xs) - padding_x,
                    0
                )


                y1 = max(
                    min(ys) - padding_y,
                    0
                )


                x2 = min(
                    max(xs) + padding_x,
                    width
                )


                y2 = min(
                    max(ys) + padding_y,
                    height
                )



                crop = frame[
                    y1:y2,
                    x1:x2
                ]



                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0,255,0),
                    3
                )


                cv2.putText(
                    frame,
                    "Object Capture Area",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0,255,0),
                    2
                )



                # Start detection timer

                if self.hand_detected_time is None:

                    self.hand_detected_time = time.time()



                # Capture after 2 seconds

                if (
                    time.time() - self.hand_detected_time > 2
                    and crop is not None
                ):

                    captured_image = crop

                    self.close_camera(
                        camera
                    )

                    break



            else:

                self.hand_detected_time = None



            cv2.imshow(
                "Astra Object Detection",
                frame
            )


            key = cv2.waitKey(1)



            # Manual capture with SPACE

            if key == 32:


                if crop is not None:

                    captured_image = crop


                self.close_camera(
                    camera
                )

                break



            # Quit

            if key == ord("q"):


                self.close_camera(
                    camera
                )

                break




        if captured_image is not None:


            path = "holding.png"


            cv2.imwrite(
                path,
                captured_image
            )


            print(
                "Captured:",
                path
            )


            return path



        return None
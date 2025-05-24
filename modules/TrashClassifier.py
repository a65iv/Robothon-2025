import cv2
import yolov5

MODEL_REF= './ai-model/yolov5s.pt'

class TrashClassifier:
    def __init__(self) -> None:
        # load model
        self.model = yolov5.load(MODEL_REF)
        # set model parameters
        self.model.conf = 0.5  # NMS confidence threshold
        self.model.iou = 0.5  # NMS IoU threshold
        self.model.agnostic = False  # NMS class-agnostic
        self.model.multi_label = False  # NMS multiple labels per box
        self.model.max_det = 1000  # maximum number of detections per image
        

    def classify(self, img_input):

        # set image
        img = img_input

        # perform inference
        results = self.model(img, size=416)

        # inference with test time augmentation
        results = self.model(img, augment=True)

        # parse results
        predictions = results.pred[0]
        boxes = predictions[:, :4] # x1, y1, x2, y2
        scores = predictions[:, 4]
        categories = predictions[:, 5]

        if len(scores) == 0:
            return None
        # get the class with the highest score
        highest_score_index = scores.argmax()
        highest_score_class = categories[highest_score_index]

        print(f"Categories: {highest_score_class}, {predictions} scores: {categories}")

        #paper = 2., plastic = 3., metal = 1., glass = 4.
        
        # results.show()
        results.print()

        if highest_score_class == 1.:
                return 'metal'
        elif highest_score_class == 2.:
                return 'paper'
        elif highest_score_class == 3.:
            return 'plastic' 
        elif highest_score_class == 0.:
            return 'glass'
        else:
            return None



classifier = TrashClassifier()

print(classifier.classify(cv2.imread("pic.png")))

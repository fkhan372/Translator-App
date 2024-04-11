#Current imports: Flask, googletrans, pillow, pytesseract

from flask import Flask, request, render_template, send_from_directory
from googletrans import Translator, LANGUAGES
from googletrans.utils import format_json
from PIL import Image
from image_languages import IMG_LANGUAGES
import cv2 as cv
import re
#UNCOMMENT TO TEST WITH EASYOCR (IMAGE TRANSLATION)
import easyocr
#UNCOMMENT TO TEST WITH PYTESSERACT(IMAGE TRANSLATION)
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = Flask(__name__, template_folder='templates')
translator = Translator()

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index2.html')
def index2():
    return render_template('index2.html', languages=LANGUAGES, detected_language=None)

@app.route('/index3.html')
def index3():
    return render_template('index3.html', languages=IMG_LANGUAGES)

@app.route('/index4.html')
def index4():
    return render_template('index4.html')

@app.route('/translate_text', methods=['POST'])
def translate_text():
    text_to_translate = request.form.get('text')
    #detected_language = translator.detect(text_to_translate).lang
    source_language = request.form.get('source_lang')
    target_language = request.form.get('target_lang')

    print(source_language)

    if source_language == "":
        detected_language = translator.detect(text_to_translate).lang
        try:
            translation = translator.translate(text_to_translate, src=detected_language, dest=target_language)
            return render_template('index2.html',
                                   translation=translation.text,
                                   original_text=text_to_translate,
                                   languages=LANGUAGES,
                                   source_language=detected_language,
                                   target_language=target_language)
        except Exception as e:
            return f"An error occurred: {e}"
    else:
        try:
            translation = translator.translate(text_to_translate, src=source_language, dest=target_language)
            return render_template('index2.html',
                                   translation=translation.text,
                                   original_text=text_to_translate,
                                   languages=LANGUAGES,
                                   source_language=source_language,
                                   target_language=target_language)
        except Exception as e:
            return f"An error occurred: {e}"

#IMAGE TRANSLATION USING PYTESSERACT
# @app.route('/translate_image', methods=['POST'])
# def translate_image():
#     try:
#         uploaded_image = request.files['image']
#         img = Image.open(uploaded_image)
#
#         # Testing refining image
#         img_test = cv.imread('static/test_images/spanish2.jpeg', cv.IMREAD_GRAYSCALE)
#         img_test2 = cv.imread('static/test_images/spanish2.jpeg')
#
#         refined_image = cv.adaptiveThreshold(img_test,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,11,2)
#         #cv.imshow('Grayscale Image - Adaptive Gaussian Thresholding', refined_image)
#         # cv.waitKey(0)
#         # cv.destroyAllWindows()
#
#         refined_image2 = cv.fastNlMeansDenoisingColored(img_test2,None,10,10,7,21)
#         #cv.imshow('De-noised Colored Image', refined_image2)
#         # cv.waitKey(0)
#         # cv.destroyAllWindows()
#
#         refined_image3 = cv.fastNlMeansDenoising(img_test,None,10,7,21)
#         #cv.imshow('De-noised Grayscale Image', refined_image3)
#         # cv.waitKey(0)
#         # cv.destroyAllWindows()
#
#         refined_image4 = cv.fastNlMeansDenoising(refined_image,None,50,7,21)
#         cv.imshow('Grayscale Image - Adaptive Gaussian Thresholding', refined_image)
#         cv.imshow('De-noised Colored Image', refined_image2)
#         cv.imshow('De-noised Grayscale Image', refined_image3)
#         cv.imshow('Grayscale Image - Adaptive Gaussian Thresholding - De-noised', refined_image4)
#         cv.waitKey(0)
#         cv.destroyAllWindows()
#
#         # MAIN TRANSLATION LOGIC
#         text_from_image = pytesseract.image_to_string(img)
#         detected_language = translator.detect(text_from_image).lang
#         translation = translator.translate(text_from_image, src=detected_language, dest='en')
#
#         filename = uploaded_image.filename
#         #print(filename)
#
#         return render_template('index3.html', extracted_text=translation.text, selected_image=filename)
#     except Exception as e:
#         return f"An error occurred: {e}"


#IMAGE TRANSLATION USING EASYOCR
@app.route('/translate_image', methods=['POST'])
def translate_image():
    try:
        source_language = request.form.get('source_lang')
        print("Selected source language: " + source_language)

        uploaded_image = request.files['image']
        img = Image.open(uploaded_image)
        print("Current image: ")
        print(img)

        filename = uploaded_image.filename
        print("Current file name: " + filename)

        reader = easyocr.Reader([source_language, 'en'], gpu=False)
        # result = reader.readtext('static/test_images/chinese2.png', detail=0)
        imageLink = 'static/test_images/' + filename
        print("Current image link: " + imageLink)
        result = reader.readtext(imageLink, detail=0)
        print("Base result:")
        print(result)

        spaceChar = "\n"
        cleaned_result = [value for value in result if not re.search(r'[0-9!@#$%^&*(),.?":;{}|<>]', value)]
        # cleaned_listToString = spaceChar.join(cleaned_result)
        print("Improved result:")
        print(cleaned_result)

        listToString = spaceChar.join(cleaned_result)
        # print(listToString)

        # MAIN TRANSLATION LOGIC
        detected_language = translator.detect(listToString).lang
        translation = translator.translate(listToString, src=detected_language, dest='en')

        filename = uploaded_image.filename

        # return render_template('index3.html', languages=LANGUAGES, extracted_text=translation.text, selected_image=filename)
        return render_template('index3.html',
                                   translation=translation.text,
                                   selected_image=filename,
                                   languages=IMG_LANGUAGES)
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)

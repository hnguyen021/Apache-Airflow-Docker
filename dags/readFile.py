# from tika import parser
# import re

# def extract_text_from_pdf(pdf_file):
#     parsed_pdf = parser.from_file(pdf_file)
#     return parsed_pdf['content']

# def split_into_sentences(text):
#     sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
#     return sentences

# def clean_sentences(sentences):
#     #words_case = {'case1': 'Ebd E-BooksDirectory.com','case2':'Part'}
#     cleaned_sentences = []
#     for sentence in sentences:
#         cleaned_sentence = ' '.join(sentence.split())  # Remove extra spaces
#         if cleaned_sentence and 'Ebd E-BooksDirectory.com' not in cleaned_sentence:  # Exclude empty sentences and the specific string
#             cleaned_sentence = re.sub(r'\bPart\s+\d+\b|[^\w\s]', '', cleaned_sentence)  # Remove 'Part' followed by a number
#             cleaned_sentence = cleaned_sentence.strip()
#             if 'CHAPTER' in cleaned_sentence:
#                 parts = re.split(r'(CHAPTER\s+\w+)', cleaned_sentence)
#                 for part in parts:
#                     if part.strip():
#                         cleaned_sentences.append(part.strip())
#             else:
#                 cleaned_sentences.append(cleaned_sentence.strip())
#     return cleaned_sentences

# pdf_content = extract_text_from_pdf('data/TSawyer.pdf')

# sentences = split_into_sentences(pdf_content)



# cleaned_sentences = clean_sentences(sentences)


# # Write cleaned sentences to a text file
# output_file = 'data/cleaned_sentences.txt'
# with open(output_file, 'w', encoding='utf-8') as file:
#     for i, sentence in enumerate(cleaned_sentences, start=1):
#         file.write(f"{sentence}\n")

# print(f"Cleaned sentences saved to '{output_file}'.")













from googletrans import Translator
import time

def translate_document(input_file, output_file, target_language='vi'):
    try:
        translator = Translator()

        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read()

        # Translate the text to Vietnamese
        translated = translator.translate(text, dest=target_language)

        # Check if the translated text is not None and write to the output file
        if translated and translated.text:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(translated.text)
            print(f"Translation complete. Translated text saved to {output_file}")
        else:
            print("Translation failed: Empty response received.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # If an error occurs, retry translation after a delay
        retry = 3  # Number of retry attempts
        for i in range(retry):
            print(f"Retrying... Attempt {i+1}/{retry}")
            time.sleep(5)  # Delay before retrying
            try:
                translated = translator.translate(text, dest=target_language)
                if translated and translated.text:
                    with open(output_file, 'w', encoding='utf-8') as file:
                        file.write(translated.text)
                    print(f"Translation successful after retry. Translated text saved to {output_file}")
                    break
                else:
                    print("Translation failed: Empty response received after retry.")
            except Exception as e:
                print(f"Retry {i+1} failed. Error: {str(e)}")
        else:
            print("Maximum retries reached. Translation failed.")


translate_document('data/cleaned_sentences.txt', 'data/output.txt')









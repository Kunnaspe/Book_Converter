import os

from django.shortcuts import render
from django.http import Http404

from novels.s3_utils import (
    list_s3_files,
    read_s3_text_file,
    generate_presigned_url,
)
from novels.nlp_utils import analyze_novel
from novels.tts_polly import text_to_mp3_polly

# shows only the first 2k characters of a novel on the details page so the browser does not try to render hundreds characters
PREVIEW_LENGTH = 2000


def novel_list(request):
    """fetch all files from the S3 and passes them to the list
    template so the user can see every available novel with size and date"""
    files = list_s3_files(prefix='raw/')
    # derives a display title from the S3 key by stripping the prefix and the file extensions so the table looks cleaner
    for f in files:
        filename = os.path.basename(f['key'])
        f['title'] = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
    context = {'files': files}
    return render(request, 'novels/list.html', context)


def novel_detail(request, s3_key):
    """reads the full text of a novel from S3 and pass a short preview to
    the detail template along with the character count so the user knows how
    large the full text is"""
    text = read_s3_text_file(s3_key)
    if text is None:
        raise Http404(f'Novel not found at key: {s3_key}')

    filename = os.path.basename(s3_key)
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

    context = {
        's3_key': s3_key,
        'title': title,
        'char_count': len(text),
        'preview': text[:PREVIEW_LENGTH],
    }
    return render(request, 'novels/detail.html', context)


def novel_analyze(request, s3_key):
    """reads the novel from S3, runs the full NLP pipeline on it and passes
    the results to the analyze template so the user can see statistics, word
    frequencies and named entities one one page"""
    text = read_s3_text_file(s3_key)
    if text is None:
        raise Http404(f'Novel not found at key: {s3_key}')

    filename = os.path.basename(s3_key)
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

    results = analyze_novel(text)

    context = {
        's3_key': s3_key,
        'title': title,
        'stats': results['stats'],
        'top_words': results['top_words'],
        'entity_counts': results['entity_counts'],
    }
    return render(request, 'novels/analyze.html', context)


def novel_tts(request, s3_key):
    """shows a voice selection form on GET and on POST calls to polly to
    generate an MP3, upload it to S3 and then show an audio player; builds
    the output key from the novel key so it is easy to find in the bucket"""
    filename = os.path.basename(s3_key)
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

    if request.method == 'POST':
        voice_id = request.POST.get('voice_id', 'Joanna')

        # reads just enough text for polly since the function will truncate but reading the whole file is fine given novel sizes
        text = read_s3_text_file(s3_key)
        if text is None:
            raise Http404(f'Novel not found at key: {s3_key}')

        # builds the output key so all the audio files land in a tts/ prefix
        base_name = os.path.splitext(filename)[0]
        s3_output_key = f'tts/{base_name}_{voice_id}.mp3'

        success, result_key = text_to_mp3_polly(
            text=text,
            s3_output_key=s3_output_key,
            voice_id=voice_id,
            engine='neural',
        )

        audio_url = None
        if success and result_key:
            # generates a presigned URL valid for one hour so the browser can play the file without credentials
            audio_url = generate_presigned_url(result_key, expiration=3600)

        context = {
            's3_key': s3_key,
            'title': title,
            'success': success,
            'audio_url': audio_url,
            'result_key': result_key,
            'voice_id': voice_id,
        }
        return render(request, 'novels/tts_result.html', context)

    # passes the s3_key and title to the form template so links are correct
    context = {
        's3_key': s3_key,
        'title': title,
    }
    return render(request, 'novels/tts_form.html', context)

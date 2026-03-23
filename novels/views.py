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

# Show only the first 2000 characters of a novel on the detail page so
# the browser does not try to render hundreds of thousands of characters
PREVIEW_LENGTH = 2000


def novel_list(request):
    """Fetch all files from the S3 raw/ prefix and pass them to the list
    template so the user can see every available novel with size and date."""
    files = list_s3_files(prefix='raw/')
    # Derive a display title from the S3 key by stripping the prefix and
    # the file extension so the table looks clean
    for f in files:
        filename = os.path.basename(f['key'])
        f['title'] = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
    context = {'files': files}
    return render(request, 'novels/list.html', context)


def novel_detail(request, s3_key):
    """Read the full text of a novel from S3 and pass a short preview to
    the detail template along with the character count so the user knows how
    large the full text is before running analysis."""
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
    """Read the novel from S3, run the full NLP pipeline on it and pass
    the results to the analyze template so the user sees statistics, word
    frequencies and named entities all on one page."""
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
    """Show a voice selection form on GET and on POST call Polly to
    generate an MP3, upload it to S3 and then show an audio player. Builds
    the output key from the novel key so it is easy to find in the bucket."""
    filename = os.path.basename(s3_key)
    title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

    if request.method == 'POST':
        voice_id = request.POST.get('voice_id', 'Joanna')

        # Read just enough text for Polly since the function will truncate
        # but reading the whole file is fine given novel sizes
        text = read_s3_text_file(s3_key)
        if text is None:
            raise Http404(f'Novel not found at key: {s3_key}')

        # Build the output key so all audio files land in a tts/ prefix
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
            # Generate a presigned URL valid for one hour so the browser
            # can play the file without needing AWS credentials
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

    # Pass the s3_key and title to the form template so links and the
    # form action URL are correct
    context = {
        's3_key': s3_key,
        'title': title,
    }
    return render(request, 'novels/tts_form.html', context)

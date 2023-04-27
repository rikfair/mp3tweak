import os.path

from pydub import AudioSegment
from pydub.utils import mediainfo
from io import BytesIO
from mutagen.mp3 import MP3
from PIL import Image
from mutagen.id3 import ID3, APIC

TAG_LIST = [
    'album',
    'album_artist',
    'artist',
    'comment',
    'composer',
    'date',
    'genre',
    'title',
    'track',
]

# -----------------------------------------------


def _add_cover(source_file, target_file):
    """ Add the cover to a file """

    tags = ID3(source_file)
    pict = tags.get("APIC:").data
    cover_img = Image.open(BytesIO(pict))
    img_byte_arr = BytesIO()
    cover_img.save(img_byte_arr, format=cover_img.format)

    audio = MP3(target_file, ID3=ID3)
    audio.tags.add(
        APIC(
            encoding=3,  # 3 is for utf-8
            mime='image/png' if cover_img.format == 'PNG' else 'image/jpeg',
            type=3,  # 3 is for the cover image
            desc=u'Cover',
            data=img_byte_arr.getvalue()
        )
    )
    audio.save(v2_version=3)


# -----------------------------------------------


def from_file(source_file, target_file=None, target_folder=None, use_tags=True, volume=0):
    """ Creates new mp3 from the source_file """

    media_info = mediainfo(source_file)

    tags = {i: media_info['TAG'].get(i, '') for i in TAG_LIST}

    # ---

    if not target_file:
        if not target_folder:
            target_folder = os.path.dirname(source_file)

        if use_tags:
            target_folder = os.path.join(target_folder, tags['album'])

        if not os.path.isdir(target_folder):
            os.makedirs(target_folder)

        target_file = os.path.join(
            target_folder,
            (f"{tags['title']}.mp3" if use_tags else os.path.basename(source_file))
        )

    # ---

    audio = AudioSegment.from_mp3(source_file)

    if volume:
        audio = audio + volume

    audio.export(
        out_f=target_file,
        format='mp3',
        bitrate=media_info['bit_rate'],
        tags=tags
    )

    # ---

    _add_cover(source_file, target_file)


# -----------------------------------------------


def from_folder(source_folder, target_folder, use_tags=True, volume=0):
    """ Creates new mp3 files for all files in a folder """

    for i in os.listdir(source_folder):
        from_file(
            source_file=os.path.join(source_folder, i),
            target_folder=target_folder,
            use_tags=use_tags,
            volume=volume
        )


# -----------------------------------------------

if __name__ == '__main__':
    from_folder(source_folder="C:/Temp/source", target_folder="C:/Temp/target", volume=10)

# -----------------------------------------------
# End.

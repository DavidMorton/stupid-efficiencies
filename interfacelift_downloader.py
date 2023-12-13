desired_aspect = 16/10
perfect_size = (2880, 1864)

from lxml.html import fromstring
import requests, re, os, time
from PIL import Image

def get_tree(baseurl):
    response = requests.get(baseurl)
    content = response.content.decode('latin-1')
    tree = fromstring(content)
    return tree

def get_best_resolution(resolutions, target_resolution):
    my_aspect_ratio = target_resolution[0] / target_resolution[1]
    
    aspect_ratios = [(x,y,x/y) for x,y in resolutions]
    aspect_ratios = list(sorted(aspect_ratios, key=lambda x:x[0] * x[1]))

    unique_aspect_ratios = list(sorted({x[2] for x in aspect_ratios}))
    best_aspect_ratios = [x for x in unique_aspect_ratios if x > my_aspect_ratio]
    if len(best_aspect_ratios) > 0:
        aspect_ratios = [x for x in aspect_ratios if x[2] == best_aspect_ratios[0]]
    else:
        best_aspect_ratio = max(unique_aspect_ratios)
        aspect_ratios = [x for x in aspect_ratios if x[2] == best_aspect_ratio]
    
    best_sizes = [(x,y) for x,y,_ in aspect_ratios if x >= target_resolution[0] and y >= target_resolution[1]]
    if len(best_sizes) > 0:
        return best_sizes[0]
    else:
        aspect_ratios = list(sorted(aspect_ratios, key=lambda x: x[0] * x[1]))
        return aspect_ratios[-1]

def get_tags(id, description):
    for _ in range(0, 5):
        try:
            response = requests.get(f'https://interfacelift.com/wallpaper/details/{id}/{description}.html')
            if response.status_code == 200:
                content = response.content.decode('latin-1')

            tree = fromstring(content)
            tags = [x.text.split('\xa0')[0] for x in tree.xpath('//*/div[@class="jeder"]/div/p/a')]
            return tags
        except:
            pass

def get_selected_tokens(baseurl):
    tree = get_tree(baseurl)

    results = []
    for select in tree.xpath('//*/select'):
        onload_tokens = select.attrib['onchange'].split("'")
        base = onload_tokens[1]
        identifier = int(onload_tokens[3])
        resolution_options = [tuple(int(_) for _ in option.attrib['value'].split('x')) for option in select.xpath('./optgroup/option')]
        resolution = get_best_resolution(resolution_options, perfect_size)
        results.append((identifier, base, resolution))
    return results

def get_selected_file(identifier, base, resolution):
    return f'{str(identifier).zfill(5)}_{base}_{resolution[0]}x{resolution[1]}.jpg'

def get_link_token():
    script_link = 'https://interfacelift.com/inc_NEW/jscript002.js'
    response = requests.get(script_link)
    content = response.content.decode()
    pattern = r"/wallpaper/([^/]+)/\""
    matcher = re.compile(pattern, re.MULTILINE)
    return matcher.findall(content)[0]

def get_download_link(token, file):
    return f'https://interfacelift.com/wallpaper/{token}/{file}'

def download_files(baseurl, target_directory, quality=90):
    files_downloaded = 0
    token = get_link_token()
    for identifier, base, resolution in get_selected_tokens(baseurl):
        basename = get_selected_file(identifier, base, resolution)
        target_filename = os.path.join(target_directory, basename)
        download_link = get_download_link(token, basename)
        os.makedirs(target_directory, exist_ok=True)
        if not os.path.exists(target_filename):
            print('Downloading', basename)
            time.sleep(0.5)
            for i in range(0, 5):
                try:
                    response = requests.get(download_link)
                    with open(target_filename, "wb") as f:
                        f.write(response.content)
                    image = Image.open(target_filename)
                    image.save(target_filename, quality=quality)
                    files_downloaded += 1
                    break
                except:
                    print("OOPS! Trying to download again...")
                    if os.path.exists(target_filename):
                        os.remove(target_filename)
                    if i == 5:
                        print('ERROR! COULD NOT DOWNLOAD FILE. STATUS CODE WAS', response.status_code)
        else:
            print('Skipping', basename, '(already exists)')
    return files_downloaded

def do_downloads(target_directory, start_page=1):
    files_downloaded = -1
    while files_downloaded != 0:
        print('Downloading page', start_page)
        if start_page == 1:
            baseurl = 'https://interfacelift.com/wallpaper/downloads/date/any/'
        else:
            baseurl = f'https://interfacelift.com/wallpaper/downloads/date/any/index{start_page}.html'
    
        files_downloaded = download_files(baseurl, target_directory)
        start_page += 1

directory = '/Users/davidmorton/Documents/Personal/Wallpapers2/'
do_downloads(directory, start_page=1)
import jinja2
import os
import urllib.request
import zipfile
import shutil

def download_test_images(DATA_PATH):
    """Download and unzip test image set from DOI 10.5447/ipk/2020/7"""

    extract_to_path = DATA_PATH
    print (extract_to_path)
    my_dir = os.path.join(extract_to_path, 'gb2_exp40', '6dai', '20190709_102939_exp40_P02-3')
    my_zip = 'images.zip'

    if not os.path.exists(my_dir):
        os.makedirs(my_dir)

    if len(os.listdir(my_dir)) != 6:
        print('=== Downloading test images ===')
        url = "http://doi.ipk-gatersleben.de/DOI/d92b5ec6-a83c-4ce6-99ab-ee4243764024/a9b2216b-4bb4-4300-8fc9-a259c485b236/2/1847940088/ZIP"
        urllib.request.urlretrieve(url, my_zip)

        with zipfile.ZipFile(my_zip) as zip_file:
            for member in zip_file.namelist():
                filename = os.path.basename(member)
                # skip directories
                if not filename:
                    continue
                # copy file (taken from zipfile's extract)
                source = zip_file.open(member)
                target = open(os.path.join(my_dir, filename), "wb")
                with source, target:
                    shutil.copyfileobj(source, target)
        os.remove(my_zip)


def create_report(plate_id, report_path):
    """Create a report for each plate with the results."""

    path = os.path.join(os.path.dirname(__file__), '.')

    templateLoader = jinja2.FileSystemLoader(searchpath=path)
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "report.html"

    image_first_lane_1 = "../" + str(plate_id) + "_1_disease_predict.png"
    image_first_lane_2 = "../" + str(plate_id) + "_1_leaf_predict.png"
    image_sec_lane_1 = "../" + str(plate_id) + "_2_disease_predict.png"
    image_sec_lane_2 = "../" + str(plate_id) + "_2_leaf_predict.png"
    image_third_lane_1 = "../" + str(plate_id) + "_3_disease_predict.png"
    image_third_lane_2 = "../" + str(plate_id) + "_3_leaf_predict.png"
    image_fourth_lane_1 = "../" + str(plate_id) + "_4_disease_predict.png"
    image_fourth_lane_2 = "../" + str(plate_id) + "_4_leaf_predict.png"

    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(plate_id=plate_id, img_id1=image_first_lane_1, img_id2=image_first_lane_2,
                                 img_id3=image_sec_lane_1, img_id4=image_sec_lane_2, img_id5=image_third_lane_1,
                                 img_id6=image_third_lane_2, img_id7=image_fourth_lane_1 ,img_id8=image_fourth_lane_2)
    # to save the results
    with open(os.path.join(report_path, plate_id + ".html"), "w") as fh:
        fh.write(outputText)


#download_test_images()
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import urllib.request
import re
import pandas
import threading


# finds all the links to the districts
def find_district_links(soup, first_district, last_district):
    district_links = []
    passed_first = False

    for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):

        # check if passed the first district link
        if link.get("href") == first_district:
            passed_first = True

        # now these are the district links, so add the link to links[]
        if passed_first:
            district_links.append(link.get('href'))

        # last link. Add it to links[] then break
        if link.get('href') == last_district:
            break
    return district_links


# takes the links for all the districts, gets all the links for the teachers in each district, and extracts the data.
def extract_data(district_links):

    # iterate through each district
    for link in district_links:

        # declare all the categories of data to be collected
        teacher_names = []
        schools = []
        districts = []
        base_salary = []
        other_salary = []
        total_final_salary = []
        insurance = []
        mandatory_benefits = []
        certificated_fte = []
        certificated_experience = []
        academic_credits = []
        classified_fte = []
        status = []
        age = []
        sex = []
        in_service_credits = []
        excess_credits = []
        highest_degree = []

        # load up the html for the district
        html_page = urllib.request.urlopen(link)
        soup = BeautifulSoup(html_page, "html.parser")

        # get the links to all the teachers in the district
        teacher_links = find_teacher_links(soup)

        # iterate through each teacher
        for teacher_link in teacher_links:

            # load up the html for the teacher
            try:
                html_page = urllib.request.urlopen(teacher_link)
            except HTTPError:
                print("HTTPError")
            soup = BeautifulSoup(html_page, "html.parser")

            # find the name of the teacher, add it to teacher_names[]
            try:
                name = soup.find("header", {"class": "entry-header"}).h1.text
                teacher_names.append(name)
            except AttributeError:
                print("Attribute error: name")
                continue

            # find div with the "datacard" because it has the school and district that the teacher is in.
            # "location" is in the format "school name" in "district name"
            try:
                data_card = soup.find("div", {"class": "data-card assignment even"})
                location = data_card.find("div", {"class": "location"}).text

                # split the location into the school and the district
                school_and_district = location.split(" in ")

                # remove the "\n" in the school name and add it to schools[]
                try:
                    school_and_district[0] = school_and_district[0].replace("\n", " ")
                    schools.append(school_and_district[0])
                except IndexError:
                    print("IndexError: School")
                    schools.append("")

                # remove the "\n" in the district name and add it to districts[]
                try:
                    school_and_district[1] = school_and_district[1].replace("\n", " ")
                    districts.append(school_and_district[1])
                except IndexError:
                    print("IndexError: District")
                    districts.append("")

            except AttributeError:
                print("AttributeError: Datacard")
                schools.append("")
                districts.append("")

            # find the data for the teacher
            divs = soup.findAll("div", {"class": "ks_half staff_detail_column"})
            # range(2) = only the previous year (there are 2 divs per year)
            for i in range(2):
                data = divs[i].findAll("div")
                for datum in data:

                    # text is in the form "label: value"
                    # ex: "Total Salary: $50,000"
                    # separate the text into label and value
                    text = datum.text
                    text = text.split(":")
                    label = text[0]
                    value = text[1]
                    value = value.replace("\n", " ")

                    # put the value into the list for the label it corresponds to
                    if label == "Base Salary":
                        base_salary.append(value)
                    if label == "Other Salary":
                        other_salary.append(value)
                    if label == "Total Final Salary":
                        total_final_salary.append(value)
                    if label == "Insurance":
                        insurance.append(value)
                    if label == "Mandatory Benefits":
                        mandatory_benefits.append(value)
                    if label == "Certificated FTE":
                        certificated_fte.append(value)
                    if label == "Certificated Experience":
                        certificated_experience.append(value)
                    if label == "Classified FTE":
                        classified_fte.append(value)
                    if label == "Academic Credits":
                        academic_credits.append(value)
                    if label == "Status":
                        status.append(value)
                    if label == "Present Age/Sex":
                        age_and_sex = value.split(" / ")
                        age.append(age_and_sex[0])
                        try:
                            sex.append(age_and_sex[1])
                        except IndexError:
                            sex.append("")
                    if label == "In-Service Credits":
                        in_service_credits.append(value)
                    if label == "ExcessCredits":
                        excess_credits.append(value)
                    if label == "Highest Degree":
                        highest_degree.append(value)

            # if a teacher did not have data for some labels, add a blank value for the missing ones
            num_values = len(base_salary)
            if len(insurance) != num_values:
                insurance.append("")
            if len(mandatory_benefits) != num_values:
                mandatory_benefits.append("")
            if len(certificated_fte) != num_values:
                certificated_fte.append("")
            if len(certificated_experience) != num_values:
                certificated_experience.append("")
            if len(classified_fte) != num_values:
                classified_fte.append("")
            if len(academic_credits) != num_values:
                academic_credits.append("")
            if len(status) != num_values:
                status.append("")
            if len(age) != num_values:
                age.append("")
            if len(sex) != num_values:
                sex.append("")
            if len(in_service_credits) != num_values:
                in_service_credits.append("")
            if len(excess_credits) != num_values:
                excess_credits.append("")
            if len(highest_degree) != num_values:
                highest_degree.append("")

        # just prints out the district
        if len(districts) != 0:
            print(districts[len(districts)-1])
        else:
            print("District empty")
            continue

        # takes all the lists of values and puts it into a csv
        to_csv(teacher_names, schools, districts, base_salary, other_salary, total_final_salary, insurance,
               mandatory_benefits, certificated_fte, certificated_experience, academic_credits, classified_fte, status,
               age, sex, in_service_credits, excess_credits, highest_degree)


# finds all the links for the teachers in a district
def find_teacher_links(soup):
    teacher_links = []

    # find all the divs
    all_divs = soup.findAll("div", {"class": "filter_target"})

    # iterate through the divs until the div with all the teacher links is found
    # div examples: "Teaching," "Principle's Office," "Instructional Professional Development," etc.
    for div in all_divs:

        # check if the div is the one with the teacher links. If it is then add all the teacher links to teacher_links[]
        if str(div.h3) == "<h3>Teaching</h3>":

            # teacher links with http
            for teacher_link in div.findAll("a", attrs={"href": re.compile("^http://")}):
                teacher_links.append(teacher_link.get("href"))

            # teacher links with https
            for teacher_link in div.findAll("a", attrs={"href": re.compile("^https://")}):
                teacher_links.append(teacher_link.get("href"))

            return teacher_links


# takes all the lists containing all the data and puts it into a dataframe.
# then turns exports the dataframe into a csv.
# this method is called for every district, so appends to the same csv.
def to_csv(teacher_names, schools, districts, base_salary, other_salary, total_final_salary, insurance,
           mandatory_benefits, certificated_fte, certificated_experience, academic_credits, classified_fte, status, age,
           sex, in_service_credits, excess_credits, highest_degree):

    # make the dataframe
    data = {"Name": teacher_names, "School": schools, "District": districts, "Base Salary": base_salary,
            "Other Salary": other_salary, "Total Final Salary": total_final_salary, "Insurance": insurance,
            "Mandatory Benefits": mandatory_benefits, "Certificated FTE": certificated_fte,
            "Certificated Experience": certificated_experience, "Classified FTE": classified_fte,
            "Academic Credits": academic_credits, "Status": status, "Age": age, "Sex": sex,
            "In-Service Credits": in_service_credits, "Excess Credits": excess_credits,
            "Highest Degree": highest_degree}
    df = pandas.DataFrame(data)

    # export to csv. Include header if it's the first district. If it's not, then append to file without headers.
    if districts[len(districts) - 1] == "Bainbridge Island School District":
        df.to_csv("WashingtonTeacherData.csv")
    else:
        df.to_csv("WashingtonTeacherData.csv", mode="a", header=False)


# threads call find_district_links with different first and last districts
def thread_init(soup, first, last):
    links = find_district_links(soup, first, last)
    print(links)
    extract_data(links)


def main():
    # load up the html for the page
    html_page = urllib.request.urlopen("http://data.kitsapsun.com/projects/wa-school/")
    soup = BeautifulSoup(html_page, "html.parser")

    # multithread

    # vader doesn't exist
    # whitepass to whitepass
    t1 = threading.Thread(target=thread_init, args=(soup, "http://data.kitsapsun.com/projects/wa-school/district/21303/"
                                                    , "http://data.kitsapsun.com/projects/wa-school/district/21303/"))

    # winlock to winlock
    t2 = threading.Thread(target=thread_init, args=(soup, "http://data.kitsapsun.com/projects/wa-school/district/21232/"
                                                    , "http://data.kitsapsun.com/projects/wa-school/district/21232/"))

    # almira to almira
    t3 = threading.Thread(target=thread_init, args=(soup, "http://data.kitsapsun.com/projects/wa-school/district/22017/"
                                                    , "http://data.kitsapsun.com/projects/wa-school/district/22017/"))

    # davenport to davenport
    t4 = threading.Thread(target=thread_init, args=(soup, "http://data.kitsapsun.com/projects/wa-school/district/22207/"
                                                    , "http://data.kitsapsun.com/projects/wa-school/district/22207/"))

    # start threads
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    print("started")

    # join threads
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    print("joined")


if __name__ == "__main__":
    main()

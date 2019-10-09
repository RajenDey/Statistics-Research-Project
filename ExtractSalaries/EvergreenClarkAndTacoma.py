import pandas


def main():
    df = pandas.read_csv("WashingtonTeacherData.csv")
    districts = df["District"]
    salary = df["Total Final Salary"]
    sex = df["Sex"]
    credits = df["In-Service Credits"]

    # get only tacoma and evergreen districts
    tacoma_salary = []
    tacoma_sex = []
    tacoma_credits = []
    evergreen_salary = []
    evergreen_sex = []
    evergreen_credits = []
    for i in range(len(districts)):
        salary1 = salary[i]
        sex1 = sex[i]
        credits1 = credits[i]
        if salary1 == "" or sex1 == "" or credits1 == "":
            continue
        if districts[i] == "Tacoma School District":
            tacoma_salary.append(salary1)
            tacoma_sex.append(sex1)
            tacoma_credits.append(credits1)
        if districts[i] == "Evergreen School District (Clark)":
            evergreen_salary.append(salary1)
            evergreen_sex.append(sex1)
            evergreen_credits.append(credits1)
    print(len(tacoma_sex))
    print(len(evergreen_sex))


if __name__ == "__main__":
    main()

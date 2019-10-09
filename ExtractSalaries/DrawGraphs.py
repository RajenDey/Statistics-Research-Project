import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import collections
from scipy import stats


# plot average teacher salary of a school with the average test score of that school
def salary_vs_test_scores(df_teachers, df_scores, subject):

    # first do the salary stuff
    salaries = df_teachers["Total Final Salary"]
    schools = df_teachers["School"]
    school_list = []
    salaries_by_school = []

    # create a 2d list of individual teacher salaries for each school
    for i in range(len(salaries)):
        if schools[i] not in school_list:
            school_list.append(schools[i])
            salaries_by_school.append([salary_to_float(salaries[i])])
        else:
            school_index = school_list.index(schools[i])
            salaries_by_school[school_index].append(salary_to_float(salaries[i]))

    # compute the average salary for that school
    average_school_salary = []
    for school in salaries_by_school:
        average_school_salary.append(int(np.mean(school)))

    # now do the test score stuff
    scores = df_scores["PercentMetStandard"]
    orgs = df_scores["OrganizationName"]
    org_level = df_scores["OrganizationLevel"]
    subjects = df_scores["TestSubject"]
    scores_by_school = []
    only_schools = []

    # create a 2d list of average test scores for each school.
    # 2d because a school may have multiple grades taking the test.
    for i in range(len(scores)):
        # Only one subject
        if org_level[i] != "School" or subjects[i] != subject or ">" in scores[i] \
                or "<" in scores[i] or scores[i] == "No Students":
            continue
        elif orgs[i] not in only_schools:
            score_float = float(scores[i].replace("%", ""))
            only_schools.append(orgs[i])
            scores_by_school.append([score_float])
        else:
            score_float = float(scores[i].replace("%", ""))
            school_index = only_schools.index(orgs[i])
            scores_by_school[school_index].append(score_float)

    # compute the average test scores for all the grades in the school
    average_scores_by_school = []
    for school in scores_by_school:
        average_scores_by_school.append(np.mean(school))

    # get rid of any schools that aren't in both datasets.
    common_schools1 = []
    common_schools2 = []
    common_average_school_salaries = []
    common_average_scores_by_school = []

    for i in range(len(school_list)):
        if i >= len(only_schools):
            break
        if school_list[i] in only_schools:
            common_schools1.append(school_list[i])
            common_schools2.append(only_schools[i])
            common_average_school_salaries.append(average_school_salary[i])
            common_average_scores_by_school.append(average_scores_by_school[i])

    # sort the average salaries and average test scores to correspond to the same school
    salary_dict = dict(zip(common_schools1, common_average_school_salaries))
    scores_dict = dict(zip(common_schools2, common_average_scores_by_school))
    sorted_salary_dict = collections.OrderedDict(sorted(salary_dict.items()))
    sorted_scores_dict = collections.OrderedDict(sorted(scores_dict.items()))
    salaries = list(sorted_salary_dict.values())
    scores = list(sorted_scores_dict.values())

    # print statistics
    slope, intercept, r, p_value, std_err = stats.linregress(salaries, scores)
    print("Slope: " + str('%.3f' % slope))
    print("Intercept: " + str('%.3f' % intercept))
    print("r: " + str('%.3f' % r))
    print("R^2: " + str('%.3f' % (r*r*100)) + " %")
    print("P Value: " + str('%.3f' % p_value))
    print("Standard Error: " + str('%.3f' % std_err))

    # plot the data and line of best fit
    plt.scatter(salaries, scores, s=1)
    plt.plot(np.unique(salaries), np.poly1d(np.polyfit(salaries, scores, 1))(np.unique(salaries)), color="red")
    plt.title("Average Test Score vs Average Teacher Salary of Washington Schools")
    plt.xlabel("Average Teacher Salary of School (Dollars)")
    plt.ylabel("Average Percentage Met Standard in School Over All Grades for " + subject)
    plt.show()


# make a histogram of all test scores
def test_scores_hist(df):
    scores = df["PercentMetStandard"]
    scores_float = []
    for score in scores:
        if ">" in score or "<" in score or score == "No Students":
            continue
        scores_float.append(float(score.replace("%", "")))

    plt.hist(scores_float, bins=80, edgecolor="black")
    plt.title("Washington Average Math, ELA, and Science Test Scores per Grade per School")
    plt.xlabel("Percent Met Standard")
    plt.show()


# make a histogram of all teacher salaries
def salary_hist(df):
    salary = df["Total Final Salary"]
    salary_float = []
    for salary_point in salary:
        salary_float.append(salary_to_float(salary_point))

    plt.hist(salary_float, bins=80, edgecolor="black")
    plt.title("Washington Teacher Salaries")
    plt.xlabel("Salary (Dollars)")
    plt.show()


# make a histogram with both male and female salaries
def male_vs_female_pay(df):
    sex = df["Sex"]
    salary = df["Total Final Salary"]
    # fte = df["Certificated FTE"]
    male_salary = []
    female_salary = []

    for i in range(len(salary)):
        # get rid of part time teachers
        # if fte[i] != 1:
        #    continue
        if sex[i] == "Male":
            male_salary.append(salary_to_float(salary[i]))
        if sex[i] == "Female":
            female_salary.append(salary_to_float(salary[i]))

    # plot male and female salaries onto the same histogram.
    # make male bars red and female bars blue.
    plt.hist(male_salary, bins=100, color="red", alpha=0.5, edgecolor="black", label="male")
    plt.hist(female_salary, bins=100, color="blue", alpha=0.5, edgecolor="black", label="female")
    plt.title("Washington Male Teacher Salaries and Female Teacher Salaries")
    plt.legend()
    plt.xlabel("Salary (Dollars)")
    plt.show()


# make a scatterplot with teacher salary and years of experience
def final_salary_vs_experience(df):
    salary = df["Total Final Salary"]
    experience = df["Certificated Experience"]
    experience_float = []
    salary_float = []

    # turn the salary and experience data from strings into floats
    for i in range(len(salary)):
        if str(experience[i]) != "" and str(experience[i]) != "nan":
            no_years = str(experience[i]).replace("years", "")
            no_space = no_years.replace(" ", "")
            experience_float.append(float(no_space))
            salary_float.append(salary_to_float(salary[i]))

    plt.scatter(experience_float, salary_float, s=.05)
    plt.plot(np.unique(experience_float), np.poly1d(np.polyfit(experience_float, salary_float, 1))
             (np.unique(experience_float)), color="red")
    plt.title("Teacher Salary vs Experience for all Washington Teachers")
    plt.xlabel("Experience (Years)")
    plt.ylabel("Salary (Dollars)")
    plt.show()


# get rid of the dollar signs, commas, and spaces in salaries
def salary_to_float(salary):
    no_dollar = salary.replace("$", "")
    no_space = no_dollar.replace(" ", "")
    no_comma = no_space.replace(",", "")
    salary_float = float(no_comma)
    return salary_float


# all the different methods and graphs
def main():
    df_teachers = pd.read_csv("WashingtonTeacherData.csv")
    df_scores = pd.read_csv("Assessment_GradeLevel_Dashboard.csv")
    final_salary_vs_experience(df_teachers)
    salary_hist(df_teachers)
    male_vs_female_pay(df_teachers)
    test_scores_hist(df_scores)
    salary_vs_test_scores(df_teachers, df_scores, "Math")


if __name__ == "__main__":
    main()

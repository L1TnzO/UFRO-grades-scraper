import requests
from bs4 import BeautifulSoup

class GradeScraper:
    def __init__(self):
        # Initialize the session and the base URL
        self.session = requests.Session()
        self.base_url = "https://intranet.ufro.cl"

    def get_grades(self, year, semester, rut, password):
        # Create the period from the year and semester
        period = year + semester

        # First request to get the session token
        login_url = self.base_url + "/autentificar.php"
        login_data = {
            "Formulario[POPUSERNAME]": rut,
            "Formulario[XYZ]": password,
        }
        self.session.post(login_url, data=login_data)

        # Second request to get the grades after logging in
        grades_url = self.base_url + "/alumno/notas/notas_sem_lst.php"
        grades_data = {
            "Formulario[periodo]": period,
            "Formulario[periodo_prm]": "",
            "Formulario[ano_nota]": "",
            "Formulario[sem_nota]": "",
            "Formulario[cod_nota]": "",
            "Formulario[mod_nota]": "",
        }
        grades_response = self.session.post(grades_url, data=grades_data)

        # Parse the HTML of the previous response
        soup = BeautifulSoup(grades_response.text, 'html.parser')

        # Find all the rows of the table that contain information of the subjects
        subject_rows = soup.select('.Tabla tr')[1:]  # Exclude the first row of headers

        # Create the list of subjects with their codes and module numbers
        subjects = []
        for row in subject_rows:
            cell_code = row.select('td a.link1')[0].text.strip()
            cell_module = int(row.select('td:nth-of-type(2)')[0].text.strip())
            subjects.append({"code": cell_code, "module": cell_module})

        # Create an empty list to store the grades
        grades = []

        for subject in subjects:
            # Request to get details of the subject
            details_url = self.base_url + "/alumno/notas/ver_notas.php"
            details_data = {
                "Formulario[periodo]": period,
                "Formulario[periodo_prm]": "",
                "Formulario[ano_nota]": year,
                "Formulario[sem_nota]": semester,
                "Formulario[cod_nota]": subject["code"],
                "Formulario[mod_nota]": str(subject["module"]),
            }
            self.session.post(details_url, data=details_data)

            # Request to get the list of grades of the subject
            list_grades_url = self.base_url + "/alumno/notas/notas_lst.php"
            list_grades_data = {
                "Formulario[periodo]": period,
            }
            list_grades_response = self.session.post(list_grades_url, data=list_grades_data)

            # Parse the HTML of the previous response
            soup = BeautifulSoup(list_grades_response.text, "html.parser")

            # Create a dictionary to store the subject information and grades
            subject_grades = {
                "code": subject["code"],
                "module": subject["module"],
                "theoretical": [],
                "practical": []
            }

            try:
                theoretical = soup.find("th", string="TeÃ³rica").find_parent("table")
                theoretical_evaluations = theoretical.find_all("tr")[2:] # Skip the first two rows that are the headers
                for evaluation in theoretical_evaluations:
                    number = evaluation.find_all("td")[0].text
                    type = evaluation.find_all("td")[1].text
                    description = evaluation.find_all("td")[2].text
                    date = evaluation.find_all("td")[3].text
                    grade = evaluation.find_all("td")[4].text
                    weight = evaluation.find_all("td")[5].text
                    # Append the evaluation to the theoretical list
                    subject_grades["theoretical"].append({
                        "number": number,
                        "type": type,
                        "description": description,
                        "date": date,
                        "grade": grade,
                        "weight": weight
                    })
            except AttributeError:
                print("Theoretical table not found")

            try:
                practical = soup.find("th", string="PrÃ¡ctica").find_parent("table")
                practical_evaluations = practical.find_all("tr")[2:] # Skip the first two rows that are the headers
                for evaluation in practical_evaluations:
                    number = evaluation.find_all("td")[0].text
                    type = evaluation.find_all("td")[1].text
                    description = evaluation.find_all("td")[2].text
                    date = evaluation.find_all("td")[3].text
                    grade = evaluation.find_all("td")[4].text
                    weight = evaluation.find_all("td")[5].text
                    # Append the evaluation to the practical list
                    subject_grades["practical"].append({
                        "number": number,
                        "type": type,
                        "description": description,
                        "date": date,
                        "grade": grade,
                        "weight": weight
                    })
            except AttributeError:
                print("Practical table not found")

            # Append the subject grades to the grades list
            grades.append(subject_grades)

            # Additional request that simulates "back" button
            grades_sem_url = self.base_url + "/alumno/notas/ver_notas_sem.php"
            self.session.post(grades_sem_url)

        # Return the grades list
        return grades


# Example usage
# Create an instance of the GradeScraper class
scraper = GradeScraper()

#Your intranet credentials
rut = ''
password = ''

#Period of your choice 
year = ''
semester = ''


grades = scraper.get_grades(year, semester, rut, password)

print(grades)
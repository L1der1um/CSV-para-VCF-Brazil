import csv
import tkinter as tk
from tkinter import filedialog, messagebox

class CSVtoVCFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV para VCF - UNIMED SOROCABA")
        self.root.geometry("400x300")
        self.root.configure(bg="#e4e0c6")

        self.frame = tk.Frame(root, bg="#e4e0c6")
        self.frame.pack(expand=True)

        self.btn_select_csv = tk.Button(self.frame, text="Selecione um CSV", command=self.select_csv_file, bg="white")
        self.btn_select_csv.pack(pady=10)

        self.btn_download_vcf = tk.Button(self.frame, text="Baixar VCF", command=self.save_vcf_file, bg="white")
        self.btn_restart = tk.Button(self.frame, text="Recomeçar", command=self.restart, bg="white")

        self.csv_file = None
        self.vcf_content = None

        # Adicionar a informação da versão no canto inferior direito
        self.version_label = tk.Label(root, text="Versão 1.11", bg="#e4e0c6", anchor='se')
        self.version_label.place(relx=1.0, rely=1.0, x=-5, y=-5, anchor='se')

    def format_phone_number(self, phone_number):
        phone_number = ''.join(filter(str.isdigit, phone_number))

        if len(phone_number) == 10:
            return '15' + phone_number
        elif len(phone_number) == 11:
            return phone_number
        elif len(phone_number) == 13 and phone_number.startswith('55'):
            return phone_number[2:]
        else:
            return '15' + phone_number

    def csv_to_vcf(self, csv_file):
        corrections = []
        vcf_entries = []
        email_variants = {'e-mail', 'email', 'e_mail'}
        with open(csv_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            headers = {header.lower(): header for header in reader.fieldnames}

            required_headers = {'first name', 'mobile phone'}
            if not required_headers.issubset(headers.keys()):
                messagebox.showerror("Erro", "Erro: Por favor altere o nome das colunas para First Name e Mobile Phone e verifique se está formatado corretamente. Exemplo: First Name, Mobile Phone")
                return None, None

            email_header = next((header for header in headers.values() if header.lower() in email_variants), None)

            for i, row in enumerate(reader, start=1):
                first_name = row[headers['first name']]
                original_phone = row[headers['mobile phone']]
                phone_number = self.format_phone_number(original_phone)

                if email_header:
                    email = row[email_header]
                else:
                    email = None

                if original_phone != phone_number:
                    corrections.append(f"Linha {i}: {original_phone} corrigido para {phone_number}")

                if phone_number:
                    vcf_entry = (
                        "BEGIN:VCARD\n"
                        "VERSION:3.0\n"
                        f"N:{first_name}\n"
                        f"FN:{first_name}\n"
                        f"TEL;TYPE=CELL:{phone_number}\n"
                    )
                    if email:
                        vcf_entry += f"EMAIL:{email}\n"
                    vcf_entry += "END:VCARD\n"
                    vcf_entries.append(vcf_entry)

        return corrections, vcf_entries

    def select_csv_file(self):
        self.csv_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not self.csv_file:
            return

        corrections, self.vcf_content = self.csv_to_vcf(self.csv_file)

        if corrections is None:
            return

        if corrections:
            correction_message = "Importante: isto não é um erro, por favor leia\n\n" + "\n".join(corrections)
        else:
            correction_message = "Importante: isto não é um erro, por favor leia\n\nNenhuma correção necessária."

        messagebox.showinfo("Correções realizadas", correction_message)
        self.btn_select_csv.pack_forget()
        self.btn_download_vcf.pack(pady=10)

    def save_vcf_file(self):
        vcf_file = filedialog.asksaveasfilename(defaultextension=".vcf", filetypes=[("VCF files", "*.vcf")])
        if not vcf_file:
            return

        with open(vcf_file, mode='w', encoding='utf-8') as outfile:
            outfile.write("\n".join(self.vcf_content))

        messagebox.showinfo("Arquivo salvo", "O arquivo VCF foi salvo com sucesso.")
        self.btn_download_vcf.pack_forget()
        self.btn_restart.pack(pady=10)

    def restart(self):
        self.btn_restart.pack_forget()
        self.btn_select_csv.pack(pady=10)

# Configuração da interface gráfica
root = tk.Tk()
app = CSVtoVCFApp(root)
root.mainloop()

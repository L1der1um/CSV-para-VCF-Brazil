import csv
import tkinter as tk
from tkinter import filedialog, messagebox

class CSVtoVCFApp:
    def __init__(self, root):

        #Configuração da janela
        self.root = root
        self.root.title("CSV para VCF - UNIMED SOROCABA")
        self.root.geometry("400x300")
        self.root.configure(bg="#2c9760")

        self.frame = tk.Frame(root, bg="#2c9760")
        self.frame.pack(expand=True)

        #Botão para solicitar um CSV
        self.btn_select_csv = tk.Button(self.frame, text="Selecione um CSV", command=self.select_csv_file, bg="white")
        self.btn_select_csv.pack(pady=10)

        #Botão para baixar o VCF gerado
        self.btn_download_vcf = tk.Button(self.frame, text="Baixar VCF", command=self.save_vcf_file, bg="white")
        #Botão para recomeçar outro CSV
        self.btn_restart = tk.Button(self.frame, text="Recomeçar", command=self.restart, bg="white")

        self.csv_file = None
        self.vcf_content = None

        #INFO VERSÃO
        self.version_label = tk.Label(root, text="Versão 1.13", bg="#2c9760", anchor='se')
        self.version_label.place(relx=1.0, rely=1.0, x=-5, y=-5, anchor='se')

    #Lógica para formatar os números de telefone
    def format_phone_number(self, phone_number):
        original_phone = phone_number
        phone_number = ''.join(filter(str.isdigit, phone_number))
        modified = False

        if len(phone_number) == 10:
            phone_number = '+5515' + phone_number
            modified = True
        elif len(phone_number) == 11:
            phone_number = '+55' + phone_number
        elif len(phone_number) == 13 and phone_number.startswith('55'):
            phone_number = '+' + phone_number
        else:
            phone_number = '+5515' + phone_number
            modified = True

        if modified or (original_phone != phone_number and (' ' in original_phone or '-' in original_phone)):
            return phone_number, True
        else:
            return phone_number, False

    #Função principal que recebe o .csv
    def csv_to_vcf(self, csv_file):
        corrections = []
        vcf_entries = []
        email_variants = {'e-mail', 'email', 'e_mail'}
        with open(csv_file, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            headers = {header.lower(): header for header in reader.fieldnames}

            #Define as colunas obrigatorias
            required_headers = {'first name', 'mobile phone'}

            #Exibe mensagem de erro caso as colunas com os nomes determinados não forem encotrados
            if not required_headers.issubset(headers.keys()):
                messagebox.showerror("Erro", "Erro: Por favor altere o nome das colunas para First Name, Mobile Phone, E-mail e verifique se está formatado corretamente (CSV). Exemplo: First Name, Mobile Phone, E-mail")
                return None, None

            #Busca as colunas dos campos
            email_header = next((header for header in headers.values() if header.lower() in email_variants), None)

            #Itera pelo .csv buscando os dados
            for i, row in enumerate(reader, start=1):
                first_name = row[headers['first name']]
                original_phone = row[headers['mobile phone']]
                phone_number, modified = self.format_phone_number(original_phone)

                if email_header:
                    email = row[email_header]
                else:
                    email = None

                #Informa o que alterou para o usuário
                if modified:
                    corrections.append(f"Linha {i}: {original_phone} corrigido para {phone_number}")

                #Base do VCF
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
    
    #Função pra encontrar o arquivo .csv
    def select_csv_file(self):
        self.csv_file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not self.csv_file:
            return

        corrections, self.vcf_content = self.csv_to_vcf(self.csv_file)

        if corrections is None:
            return

        #Exibe mensagem das correções que foram realizadas
        if corrections:
            correction_message = "Importante: isto não é um erro, por favor leia\n\n" + "\n".join(corrections)
        else:
            correction_message = "Importante: isto não é um erro, por favor leia\n\nNenhuma correção necessária."

        #Exibe mensagem das correções que foram realizadas
        messagebox.showinfo("Correções realizadas", correction_message)
        self.btn_select_csv.pack_forget()
        self.btn_download_vcf.pack(pady=10)

    #Função chamada botão para baixar o VCF
    def save_vcf_file(self):
        vcf_file = filedialog.asksaveasfilename(defaultextension=".vcf", filetypes=[("VCF files", "*.vcf")])
        if not vcf_file:
            return

        with open(vcf_file, mode='w', encoding='utf-8') as outfile:
            outfile.write("\n".join(self.vcf_content))

        #Exibe mensagem de que o arquivo foi salvo
        messagebox.showinfo("Arquivo salvo", "O arquivo VCF foi salvo com sucesso.")
        self.btn_download_vcf.pack_forget()
        self.btn_restart.pack(pady=10)

    #Função chama botão Restart
    def restart(self):
        self.btn_restart.pack_forget()
        self.btn_select_csv.pack(pady=10)


#Configuração da interface gráfica
root = tk.Tk()
app = CSVtoVCFApp(root)
root.mainloop()

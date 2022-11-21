# -*- coding: utf-8 -*-
import xlsxwriter
from io import BytesIO
from datetime import datetime
import base64
import os
from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError, AccessError


numbers = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤', '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩', '.': '.'}


class ReportExcel(models.TransientModel):
    _name = 'report.excel'

    excel_file = fields.Binary('Download report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)


class SocialInsuranceWizard(models.TransientModel):
    _name = 'social.insurance.wizard'

    excel_file = fields.Binary('Download report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)
    choose_employee = fields.Selection([('all_employees', 'ALL Employees'), ('specific_employee', 'Specific Employee')],
                                       string='Choose Employee ', required=True, default='all_employees')

    specific_employee = fields.Many2many('hr.employee', string='Specific Employee')



    def translate_number(self, string):
        h = []
        for m in string:
            if m in numbers.keys():
                n = numbers[m]
                h.append(n)
            else:
                h.append(' ')
        return ''.join(h)

    def action_social_insurance_report(self):
        data = []
        dic = {}

        if self.choose_employee == 'all_employees':
            employee = self.env['hr.employee'].search([(1, '=', 1)])
            employee = employee.sorted(key=lambda r: int(r.social_number))
            for rec in employee:
                if rec.social_company_id:
                    for line in employee.social_company_id:
                        if rec.social_company_id.id == line.id:
                            break
                        else:
                            raise ValidationError('Employees must be in one company')
        else:
            employee = self.specific_employee
            employee = employee.sorted(key=lambda r: int(r.social_number))

        for m in employee:
            if m.arabic_name:
                dic['name'] = m.arabic_name
                dic['social_number'] = self.translate_number(str(m.social_number))
                dic['identification_id'] = self.translate_number(str(m.identification_id))
                dic['social_date'] = m.social_date
                dic['social_company_id'] = m.social_company_id.social_number
                # dic['social_company_id'] = m.social_company_id.name
                # dic['basic_insurance_salary'] = self.translate_number(str(1670))
                # dic['basic_insurance_salary'] = self.translate_number(str(m.basic_insurance_salary))
                contract = self.env['hr.contract'].search([('employee_id', '=', m.id), ('state', '=', 'open')], limit=1)
                for n in contract:
                    dic['wage'] = self.translate_number(str(round(n.wage, 2)))
                    dic['insurance_amount'] = self.translate_number(str(round(n.fixed_insurance, 2)))
                    dic['all_amount'] = round(n.wage / n.currency_id.rate, 2)
                    dic['all_amount'] = self.translate_number(str(dic['all_amount']))
                    dic['all_insurance_amount'] = round(n.fixed_insurance, 2)
                data.append(dic)
                dic = {}

        if data:
            act = self.generate_excel(data)

            return {

                'type': 'ir.actions.act_window',
                'res_model': 'report.excel',
                'res_id': act.id,
                'view_type': 'form',
                'view_mode': 'form',
                'context': self.env.context,
                'target': 'new',

            }
        else:
            raise ValidationError(_('No Records To Show'))






    def generate_excel(self, data):

        filename = 'Social Insurance '
        output = BytesIO()
        all_insurance_amount = 0
        for rec in data:
            all_insurance_amount += rec['all_insurance_amount'] if 'all_insurance_amount' in rec else 0
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        for item in range(0,len(data),10):
            records = data[item:item+10]
            sheet = workbook.add_worksheet('Social Insurance {}'.format((item / 10) + 1))
            without_borders = workbook.add_format({
                'bold': 1,
                'border': 0,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'font_size': '11',

            })

            font_size_10 = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 15, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 0})
            font_size_10.set_reading_order(2)
            font_size_11 = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 15, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})
            font_size_12 = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 13, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})
            font_size_green = workbook.add_format(
                {'font_name': 'KacstBook', 'bg_color': '#008000', 'font_size': 10, 'align': 'center',
                 'valign': 'vcenter',
                 'text_wrap': True,
                 'border': 1})

            table_header_formate = workbook.add_format({
                'bold': 1,
                'border': 1,
                'bg_color': '#AAB7B8',
                'font_size': '10',
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            })
            row = 13

            col = 23
            k = len(data)
            sheet.set_column(9, 22, 2, without_borders)
            sheet.set_column(24, 31, 2, without_borders)
            sheet.set_column(23, 23, 30, without_borders)

            sheet.merge_range('Y1:AG1', 'الهيئة القومية للتامين الاجتماعي', font_size_10)
            sheet.merge_range('Y2:AG2', 'صندوق العاملين بقطاع الاعمال والخاص', font_size_10)
            sheet.merge_range('Y3:AG3', 'منطقة :شرق مدينة نصر', font_size_10)
            sheet.merge_range('Y4:AG4', 'مكتب : مدينة نصر اول', font_size_10)
            sheet.merge_range('M2:P2', 'رقم المنشأة :', font_size_10)
            sheet.merge_range('F4:W4',
                              '	طلب إشتراك منشأة أو إخطار تعديل بيانات المؤمن عليهم وأجورهم في   /    /     ٢٠ م',
                              font_size_10)
            sheet.merge_range('A6:AF6',
                              'اسم المنشأة:   شور العالمية للتقنية                                                                 المالك / المدير المسئول :   ايهاب عبدالواحد مصطفي                          الشكل القانوني للمنشأة:ذات مسؤلية محدودة',
                              font_size_10)
            sheet.merge_range('A8:AF8',
                              'عنوان المنشأة:  56                  اسم الشارع:  عباس العقاد                                  الشياخة / القرية:    مدينة نصر اول                      القسم / المركز:                           المحافظة: القاهرة',
                              font_size_10)
            sheet.merge_range('A9:AF9',
                              'نسبة تأمين المرض:                   تاريخ بدء النسبة:      /       /        ٢٠م.             نسبة تأمين الإصابة:                    تاريخ بدء النسبة:      /       /        ٢٠م.',
                              font_size_10)
            sheet.merge_range('A10:AF10',
                              'تاريخ التوقف/الاستمرار:     /      /      ٢٠م.    سبب التوقف:                     .بدء النشاط: ١٩٩٩/٠٢/٠١                         .رقم التسجيل الضريبي للمنشأة:               /             /',
                              font_size_10)
            for rec in records:
                all_insurance_amount += rec['all_insurance_amount'] if 'all_insurance_amount' in rec else 0
                sheet.write(row, col, str(rec['name']) or '', font_size_11)
                if rec['social_number']:
                    for m in range(0, len(str(rec['social_number']))):
                        sheet.write(row, col + 1 + m, str(rec['social_number'][m]) or '', font_size_12)
                if rec['identification_id']:
                    for m in range(0, len(str(rec['identification_id']))):
                        sheet.write(row, col - 14 + m, str(rec['identification_id'][m]) or '', font_size_12)
                if rec['social_date']:
                    sheet.write(row, col - 17, self.translate_number(str(rec['social_date'].year)) or '',
                                font_size_12)
                    sheet.write(row, col - 16, self.translate_number(str(rec['social_date'].month)) or '',
                                font_size_12)
                    sheet.write(row, col - 15, self.translate_number(str(rec['social_date'].day)) or '',
                                font_size_12)
                # index = str(rec['basic_insurance_salary']).find('.')
                # if index == -1:
                #     sheet.write(row, col - 19, str(rec['basic_insurance_salary']) or '', font_size_12)
                #     sheet.write(row, col - 18, str('٠') or '', font_size_12)
                # else:
                #     sheet.write(row, col - 19, str(rec['basic_insurance_salary'])[0:index] or '', font_size_12)
                #     sheet.write(row, col - 18, str(rec['basic_insurance_salary'])[index + 1:] or '', font_size_12)
                if 'insurance_amount' in rec:
                    index = str(rec['insurance_amount']).find('.')
                    if index == -1:
                        sheet.write(row, col - 21, str(rec['insurance_amount']) or '', font_size_12)
                        sheet.write(row, col - 20, str('٠') or '', font_size_12)
                    else:
                        sheet.write(row, col - 21, str(rec['insurance_amount'])[0:index] or '', font_size_12)
                        sheet.write(row, col - 20, str(rec['insurance_amount'])[index + 1:] or '', font_size_12)
                if 'all_amount' in rec:
                    index = str(rec['all_amount']).find('.')
                    if index == -1:
                        sheet.write(row, col - 23, str(rec['all_amount']) or '', font_size_12)
                        sheet.write(row, col - 22, str('٠') or '', font_size_12)
                    else:
                        sheet.write(row, col - 23, str(rec['all_amount'])[0:index] or '', font_size_12)
                        sheet.write(row, col - 22, str(rec['all_amount'])[index + 1:] or '', font_size_12)

                row += 1
            b = row + 1
            for m in range(0, b + 6):
                sheet.set_row(m, 20)
            all_insurance_amount_str = self.translate_number(str(round(all_insurance_amount, 2)))
            index = str(all_insurance_amount_str).find('.')
            if index == -1:
                pound = all_insurance_amount_str
                cent = str('٠')
            else:
                pound = all_insurance_amount_str[0:index]
                cent = all_insurance_amount_str[index + 1:]
            sheet.merge_range('A%s:AF%s' % (b, b),
                              '       أقر أنا :  ايهاب عبدالواحد مصطفي                            بصفتى :المدير المسئول                         بأن اجمالى أعداد المؤمن عليهم : %s  عاملاً .' % (
                                  self.translate_number(str(k))),
                              font_size_10)
            sheet.merge_range('A%s:AF%s' % (b + 2, b + 2),
                              '   وأن أجور الشهر الحالى :                                      {}    {}                    . وأن جميع البيانات الواردة بهذه الاستمارة وملحقاتها صحيحة .(الاجر الشامل لحساب اشتراكات التأمين الصحى الشامل) '.format(
                                  cent, pound),
                              font_size_10)
            sheet.merge_range('A%s:AF%s' % (b + 3, b + 3),
                              '    صاحب العمل أو المدير المسؤول :                             . روجعت بيانات هذا الطلب على طلبات اشتراك المؤمن عليهم ووجدت صحيحة (الاجر الشامل لحساب اشتراكات التأمين الصحى الشامل)  ',
                              font_size_10)
            sheet.merge_range('A%s:AF%s' % (b + 4, b + 4),
                              '  مستلم الاستمارة : ........................................  . تم مطابق لتوقيع بمعرفتى : ................................................  ',
                              font_size_10)
            sheet.merge_range('A%s:AF%s' % (b + 5, b + 5),
                              ' اخصائى الاشتراك : ....................................... سجل الياً : .......................................... روجع الياً : ......................................... ',
                              font_size_10)
            sheet.merge_range('A%s:AF%s' % (b + 6, b + 6), ' تحريراً فى :  ', font_size_10)
            sheet.merge_range('T%s:U%s' % (b + 1, b + 1), 'جنيه', font_size_10)
            sheet.merge_range('V%s:W%s' % (b + 1, b + 1), 'قرش', font_size_10)
            sheet.merge_range('Y12:AF13', 'الرقم التاميني', font_size_11)
            sheet.merge_range('J12:W13', 'الرقم القومي', font_size_11)
            sheet.merge_range('X12:X13', 'اسم المؤمن عليه', font_size_11)
            sheet.merge_range('G12:I12', 'تاريخ الالتحاق', font_size_11)
            sheet.merge_range('E12:F12', 'الاجر الاساسى', font_size_11)
            sheet.merge_range('C12:D12', 'اجر الاشترك التامين', font_size_11)
            sheet.merge_range('A12:B12', 'الاجر الشامل', font_size_11)
            sheet.write('I13', 'يوم ', font_size_11)
            sheet.write('H13', 'شهر', font_size_11)
            sheet.write('G13', 'سنة', font_size_11)
            sheet.write('F13', 'قرش', font_size_11)
            sheet.write('E13', 'جنيه', font_size_11)
            sheet.write('D13', 'قرش', font_size_11)
            sheet.write('C13', 'جنيه', font_size_11)
            sheet.write('B13', 'قرش', font_size_11)
            sheet.write('A13', 'جنيه', font_size_11)
            column = 0
            for line in str(data[0]['social_company_id']):
                sheet.write(1, column,line ,font_size_11)
                column += 1

            full_path = os.path.realpath(__file__)

            print("This file directory only")
            print(os.path.dirname(full_path))
            sheet.insert_image(0, 23, os.path.dirname(full_path) + '/f.png')

            row = 1
            for rec in data:
                row += 1

        workbook.close()
        output.seek(0)

        self.write({'file_name': filename + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'})
        self.excel_file = base64.b64encode(output.read())

        context = {
            'file_name': self.file_name,
            'excel_file': self.excel_file,
        }

        act_id = self.env['report.excel'].create(context)
        return act_id
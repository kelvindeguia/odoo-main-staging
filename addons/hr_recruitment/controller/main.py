from odoo import http
from odoo.http import request
from odoo.http import Response
import base64

class WebsiteFormController(http.Controller):
    @http.route('/referral/', type='http', auth="public", website=True)
    def website_form(self, **post):
        # Render the form template again
        return http.request.render('hr_recruitment.referral_page')

    @http.route('/referral/website_thanks/', type='http', auth='public', website=True)
    def referral_website_thanks(self, **post):
        # Extract data from the form submission
        emp_name = post.get('emp_name')
        employee_email = post.get('employee_email')
        emp_id = post.get('emp_id')
        emp_account = post.get('emp_account')
        name = post.get('name')
        email = post.get('email')
        mobile_number = post.get('mobile_number')
        desired_position = post.get('desired_position')
        job_id = post.get('job_id')
        department_id = post.get('department_id')
        
        # Retrieve the job data from the session
        job_id_from_session = request.session.get('job_id')
        department_id_from_session = request.session.get('department_id')
        job_name_from_session = request.session.get('job_name')
        
        if job_id_from_session:
            # Fetch the job object (optional, if you need it to fetch other details)
            job = request.env['hr.job'].sudo().browse(job_id_from_session)
            
        if job_name_from_session:
            # Fetch the job object (optional, if you need it to fetch other details)
            job_name = request.env['hr.job'].sudo().browse(job_name_from_session)
            
        if department_id_from_session:
            # Fetch the job object (optional, if you need it to fetch other details)
            department = request.env['hr.job'].sudo().browse(department_id_from_session)
        
        # Check for existing records
        existing_referrals = http.request.env['hr.referral'].sudo().search([
            '|',
            ('email', '=', email),
            ('mobile_number', '=', mobile_number),
            # ('record_ageing_ref', '<', 90)
        ])

        existing_referrals_applicant = http.request.env['hr.applicant'].sudo().search([
            '|',
            ('email_from', '=', email),
            ('x_mobile_number', '=', mobile_number),
            # ('record_ageing_ref', '<', 90)
        ])

        blacklisted_applicant = http.request.env['hr.blacklist'].sudo().search([
            ('email', '=', email),
            # ('record_ageing_ref', '<', 90)
        ])

        if existing_referrals or existing_referrals_applicant or blacklisted_applicant:
            error_message = "Duplicate entry found. Please ensure your data is unique."
            return http.request.render("hr_recruitment.duplicate_entry", {'error_message': error_message})

        # Handle the uploaded resume
        resume = http.request.httprequest.files.get('resume')
        resume_data = None
        if resume:
            resume_name = resume.filename
            resume_data = resume.read()

        # Find the user by name
        user_name = "Referral"
        user = http.request.env['res.users'].sudo().search([('name', '=', user_name)], limit=1)

        # Create a new hr.referral record with the extracted data
        referral_data = {
            'emp_name': emp_name,
            'employee_email': employee_email,
            'emp_id': emp_id,
            'emp_account': emp_account,
            'name': name,
            'email': email,
            'mobile_number': mobile_number,
            'desired_position': desired_position,
            'job_id': job_id,
            'department_id': department_id,
            'referral_ids': [(0, 0, {
                'name': resume_name,
                'res_model': 'hr.referral',
                'res_id': 0,
                'type': 'binary',
                'datas': base64.b64encode(resume_data),
                'mimetype': 'application/pdf',
            })] if resume_data else [],
            'user_id': user.id if user else False,
        }

        referral = http.request.env['hr.referral'].sudo().create(referral_data)

        # Continue with any additional actions or responses
        # For example, you can display a thank-you message
        return http.request.render("hr_recruitment.referral_thanks", {})
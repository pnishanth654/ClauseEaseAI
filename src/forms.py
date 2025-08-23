from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp
import phonenumbers

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(min=2, max=50, message="First name must be between 2 and 50 characters")])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(min=1, max=50, message="Last name must be between 1 and 50 characters")])
    email = StringField("Email", validators=[DataRequired(), Email(message="Invalid email")])
    country_code = SelectField("Country Code", choices=[
        ('+91', 'India (+91)'),
        ('+1', 'USA (+1)'),
        ('+44', 'UK (+44)'),
        ('+61', 'Australia (+61)'),
        ('+49', 'Germany (+49)'),
        ('+33', 'France (+33)'),
        ('+39', 'Italy (+39)'),
        ('+34', 'Spain (+34)'),
        ('+81', 'Japan (+81)'),
        ('+86', 'China (+86)'),
        ('+82', 'South Korea (+82)'),
        ('+65', 'Singapore (+65)'),
        ('+971', 'UAE (+971)'),
        ('+966', 'Saudi Arabia (+966)'),
        ('+27', 'South Africa (+27)'),
        ('+55', 'Brazil (+55)'),
        ('+52', 'Mexico (+52)'),
        ('+54', 'Argentina (+54)'),
        ('+56', 'Chile (+56)'),
        ('+57', 'Colombia (+57)'),
        ('+31', 'Netherlands (+31)'),
        ('+46', 'Sweden (+46)'),
        ('+47', 'Norway (+47)'),
        ('+45', 'Denmark (+45)'),
        ('+358', 'Finland (+358)'),
        ('+41', 'Switzerland (+41)'),
        ('+43', 'Austria (+43)'),
        ('+32', 'Belgium (+32)'),
        ('+48', 'Poland (+48)'),
        ('+420', 'Czech Republic (+420)'),
        ('+36', 'Hungary (+36)'),
        ('+40', 'Romania (+40)'),
        ('+30', 'Greece (+30)'),
        ('+351', 'Portugal (+351)'),
        ('+353', 'Ireland (+353)'),
        ('+354', 'Iceland (+354)'),
        ('+64', 'New Zealand (+64)'),
        ('+60', 'Malaysia (+60)'),
        ('+62', 'Indonesia (+62)'),
        ('+63', 'Philippines (+63)'),
        ('+66', 'Thailand (+66)'),
        ('+84', 'Vietnam (+84)'),
        ('+92', 'Pakistan (+92)'),
        ('+880', 'Bangladesh (+880)'),
        ('+977', 'Nepal (+977)'),
        ('+94', 'Sri Lanka (+94)'),
        ('+95', 'Myanmar (+95)'),
        ('+960', 'Maldives (+960)'),
        ('+975', 'Bhutan (+975)'),
        ('+856', 'Laos (+856)'),
        ('+855', 'Cambodia (+855)'),
        ('+976', 'Mongolia (+976)'),
        ('+7', 'Kazakhstan (+7)'),
        ('+996', 'Kyrgyzstan (+996)'),
        ('+992', 'Tajikistan (+992)'),
        ('+993', 'Turkmenistan (+993)'),
        ('+998', 'Uzbekistan (+998)'),
        ('+994', 'Azerbaijan (+994)'),
        ('+374', 'Armenia (+374)'),
        ('+995', 'Georgia (+995)'),
        ('+98', 'Iran (+98)'),
        ('+964', 'Iraq (+964)'),
        ('+962', 'Jordan (+962)'),
        ('+961', 'Lebanon (+961)'),
        ('+963', 'Syria (+963)'),
        ('+967', 'Yemen (+967)'),
        ('+973', 'Bahrain (+973)'),
        ('+965', 'Kuwait (+965)'),
        ('+974', 'Qatar (+974)'),
        ('+968', 'Oman (+968)'),
        ('+972', 'Israel (+972)'),
        ('+90', 'Turkey (+90)'),
        ('+20', 'Egypt (+20)'),
        ('+212', 'Morocco (+212)'),
        ('+213', 'Algeria (+213)'),
        ('+216', 'Tunisia (+216)'),
        ('+218', 'Libya (+218)'),
        ('+222', 'Mauritania (+222)'),
        ('+221', 'Senegal (+221)'),
        ('+233', 'Ghana (+233)'),
        ('+234', 'Nigeria (+234)'),
        ('+254', 'Kenya (+254)'),
        ('+255', 'Tanzania (+255)'),
        ('+256', 'Uganda (+256)'),
        ('+251', 'Ethiopia (+251)'),
        ('+249', 'Sudan (+249)'),
        ('+250', 'Rwanda (+250)'),
        ('+257', 'Burundi (+257)'),
        ('+236', 'Central African Republic (+236)'),
        ('+235', 'Chad (+235)'),
        ('+237', 'Cameroon (+237)'),
        ('+238', '🇨🇻 Cape Verde (+238)'),
        ('+239', '🇸🇹 São Tomé and Príncipe (+239)'),
        ('+240', '🇬🇶 Equatorial Guinea (+240)'),
        ('+241', '🇬🇦 Gabon (+241)'),
        ('+242', '🇨🇬 Congo (+242)'),
        ('+243', '🇨🇩 Democratic Republic of Congo (+243)'),
        ('+244', '🇦🇴 Angola (+244)'),
        ('+245', '🇬🇼 Guinea-Bissau (+245)'),
        ('+246', '🇮🇴 British Indian Ocean Territory (+246)'),
        ('+247', '🇦🇨 Ascension (+247)'),
        ('+248', '🇸🇨 Seychelles (+248)'),
        ('+249', '🇸🇩 Sudan (+249)'),
        ('+250', '🇷🇼 Rwanda (+250)'),
        ('+251', '🇪🇹 Ethiopia (+251)'),
        ('+252', '🇸🇴 Somalia (+252)'),
        ('+253', '🇩🇯 Djibouti (+253)'),
        ('+254', '🇰🇪 Kenya (+254)'),
        ('+255', '🇹🇿 Tanzania (+255)'),
        ('+256', '🇺🇬 Uganda (+256)'),
        ('+257', '🇧🇮 Burundi (+257)'),
        ('+258', '🇲🇿 Mozambique (+258)'),
        ('+260', '🇿🇲 Zambia (+260)'),
        ('+261', '🇲🇬 Madagascar (+261)'),
        ('+262', '🇷🇪 Réunion (+262)'),
        ('+263', '🇿🇼 Zimbabwe (+263)'),
        ('+264', '🇳🇦 Namibia (+264)'),
        ('+265', '🇲🇼 Malawi (+265)'),
        ('+266', '🇱🇸 Lesotho (+266)'),
        ('+267', '🇧🇼 Botswana (+267)'),
        ('+268', '🇸🇿 Eswatini (+268)'),
        ('+269', '🇰🇲 Comoros (+269)'),
        ('+290', '🇸🇭 Saint Helena (+290)'),
        ('+291', '🇪🇷 Eritrea (+291)'),
        ('+297', '🇦🇼 Aruba (+297)'),
        ('+298', '🇫🇴 Faroe Islands (+298)'),
        ('+299', '🇬🇱 Greenland (+299)'),
        ('+350', '🇬🇮 Gibraltar (+350)'),
        ('+351', '🇵🇹 Portugal (+351)'),
        ('+352', '🇱🇺 Luxembourg (+352)'),
        ('+353', '🇮🇪 Ireland (+353)'),
        ('+354', '🇮🇸 Iceland (+354)'),
        ('+355', '🇦🇱 Albania (+355)'),
        ('+356', '🇲🇹 Malta (+356)'),
        ('+357', '🇨🇾 Cyprus (+357)'),
        ('+358', '🇫🇮 Finland (+358)'),
        ('+359', '🇧🇬 Bulgaria (+359)'),
        ('+370', '🇱🇹 Lithuania (+370)'),
        ('+371', '🇱🇻 Latvia (+371)'),
        ('+372', '🇪🇪 Estonia (+372)'),
        ('+373', '🇲🇩 Moldova (+373)'),
        ('+374', '🇦🇲 Armenia (+374)'),
        ('+375', '🇧🇾 Belarus (+375)'),
        ('+376', '🇦🇩 Andorra (+376)'),
        ('+377', '🇲🇨 Monaco (+377)'),
        ('+378', '🇸🇲 San Marino (+378)'),
        ('+379', '🇻🇦 Vatican City (+379)'),
        ('+380', '🇺🇦 Ukraine (+380)'),
        ('+381', '🇷🇸 Serbia (+381)'),
        ('+382', '🇲🇪 Montenegro (+382)'),
        ('+383', '🇽🇰 Kosovo (+383)'),
        ('+385', '🇭🇷 Croatia (+385)'),
        ('+386', '🇸🇮 Slovenia (+386)'),
        ('+387', '🇧🇦 Bosnia and Herzegovina (+387)'),
        ('+389', '🇲🇰 North Macedonia (+389)'),
        ('+420', '🇨🇿 Czech Republic (+420)'),
        ('+421', '🇸🇰 Slovakia (+421)'),
        ('+423', '🇱🇮 Liechtenstein (+423)'),
        ('+500', '🇫🇰 Falkland Islands (+500)'),
        ('+501', '🇧🇿 Belize (+501)'),
        ('+502', '🇬🇹 Guatemala (+502)'),
        ('+503', '🇸🇻 El Salvador (+503)'),
        ('+504', '🇭🇳 Honduras (+504)'),
        ('+505', '🇳🇮 Nicaragua (+505)'),
        ('+506', '🇨🇷 Costa Rica (+506)'),
        ('+507', '🇵🇦 Panama (+507)'),
        ('+508', '🇵🇲 Saint Pierre and Miquelon (+508)'),
        ('+509', '🇭🇹 Haiti (+509)'),
        ('+590', '🇬🇵 Guadeloupe (+590)'),
        ('+591', '🇧🇴 Bolivia (+591)'),
        ('+592', '🇬🇾 Guyana (+592)'),
        ('+593', '🇪🇨 Ecuador (+593)'),
        ('+594', '🇬🇫 French Guiana (+594)'),
        ('+595', '🇵🇾 Paraguay (+595)'),
        ('+596', '🇲🇶 Martinique (+596)'),
        ('+597', '🇸🇷 Suriname (+597)'),
        ('+598', '🇺🇾 Uruguay (+598)'),
        ('+599', '🇧🇶 Caribbean Netherlands (+599)'),
        ('+670', '🇹🇱 East Timor (+670)'),
        ('+672', '🇦🇶 Australian Antarctic Territory (+672)'),
        ('+673', '🇧🇳 Brunei (+673)'),
        ('+674', '🇳🇷 Nauru (+674)'),
        ('+675', '🇵🇬 Papua New Guinea (+675)'),
        ('+676', '🇹🇴 Tonga (+676)'),
        ('+677', '🇸🇧 Solomon Islands (+677)'),
        ('+678', '🇻🇺 Vanuatu (+678)'),
        ('+679', '🇫🇯 Fiji (+679)'),
        ('+680', '🇵🇼 Palau (+680)'),
        ('+681', '🇼🇫 Wallis and Futuna (+681)'),
        ('+682', '🇨🇰 Cook Islands (+682)'),
        ('+683', '🇳🇺 Niue (+683)'),
        ('+685', '🇼🇸 Samoa (+685)'),
        ('+686', '🇰🇮 Kiribati (+686)'),
        ('+687', '🇳🇨 New Caledonia (+687)'),
        ('+688', '🇹🇻 Tuvalu (+688)'),
        ('+689', '🇵🇫 French Polynesia (+689)'),
        ('+690', '🇹🇰 Tokelau (+690)'),
        ('+691', '🇫🇲 Micronesia (+691)'),
        ('+692', '🇲🇭 Marshall Islands (+692)'),
        ('+850', '🇰🇵 North Korea (+850)'),
        ('+852', '🇭🇰 Hong Kong (+852)'),
        ('+853', '🇲🇴 Macau (+853)'),
        ('+855', '🇰🇭 Cambodia (+855)'),
        ('+856', '🇱🇦 Laos (+856)'),
        ('+880', '🇧🇩 Bangladesh (+880)'),
        ('+886', '🇹🇼 Taiwan (+886)'),
        ('+960', '🇲🇻 Maldives (+960)'),
        ('+961', '🇱🇧 Lebanon (+961)'),
        ('+962', '🇯🇴 Jordan (+962)'),
        ('+963', '🇸🇾 Syria (+963)'),
        ('+964', '🇮🇶 Iraq (+964)'),
        ('+965', '🇰🇼 Kuwait (+965)'),
        ('+966', '🇸🇦 Saudi Arabia (+966)'),
        ('+967', '🇾🇪 Yemen (+967)'),
        ('+968', '🇴🇲 Oman (+968)'),
        ('+970', '🇵🇸 Palestine (+970)'),
        ('+971', '🇦🇪 UAE (+971)'),
        ('+972', '🇮🇱 Israel (+972)'),
        ('+973', '🇧🇭 Bahrain (+973)'),
        ('+974', '🇶🇦 Qatar (+974)'),
        ('+975', '🇧🇹 Bhutan (+975)'),
        ('+976', '🇲🇳 Mongolia (+976)'),
        ('+977', '🇳🇵 Nepal (+977)'),
        ('+992', '🇹🇯 Tajikistan (+992)'),
        ('+993', '🇹🇲 Turkmenistan (+993)'),
        ('+994', '🇦🇿 Azerbaijan (+994)'),
        ('+995', '🇬🇪 Georgia (+995)'),
        ('+996', '🇰🇬 Kyrgyzstan (+996)'),
        ('+998', '🇺🇿 Uzbekistan (+998)'),
    ], default='+91')
    phone = StringField("Phone Number", validators=[DataRequired(), Regexp(r'^\d{10}$', message="Please enter exactly 10 digits")])
    gender = SelectField("Gender", choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[DataRequired(message="Please select your gender")])
    date_of_birth = StringField("Date of Birth", validators=[DataRequired(message="Please enter your date of birth")], render_kw={"type": "date"})
    password = PasswordField("Password", validators=[
        DataRequired(), 
        Length(min=8, message="Password must be at least 8 characters"),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$', 
               message="Password must contain uppercase, lowercase, number, and special character")
    ])
    submit = SubmitField("Create account")

    def validate(self, extra_validators=None):
        if not super().validate():
            return False
        
        # Both email and phone are now mandatory
        if not self.email.data:
            self.email.errors.append("Email is required.")
            return False
        
        if not self.phone.data:
            self.phone.errors.append("Phone number is required.")
            return False
        
        # Validate phone number format
        if self.phone.data:
            # Combine country code with phone number
            full_phone = self.country_code.data + self.phone.data
            try:
                parsed = phonenumbers.parse(full_phone, None)
                if not phonenumbers.is_valid_number(parsed):
                    self.phone.errors.append("Invalid phone number")
                    return False
                # Don't modify self.phone.data here - keep the 10-digit input
                # The combination will be done in app.py before saving to database
            except Exception:
                self.phone.errors.append("Invalid phone number")
                return False
        return True

class LoginForm(FlaskForm):
    identifier = StringField("Email or Phone", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")

class ForgotPasswordForm(FlaskForm):
    identifier = StringField("Email or Phone", validators=[DataRequired()])
    submit = SubmitField("Send reset link")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[
        DataRequired(), 
        Length(min=8, message="Password must be at least 8 characters"),
        Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])[A-Za-z\d!@#$%^&*(),.?":{}|<>]{8,}$', 
               message="Password must contain uppercase, lowercase, number, and special character")
    ])
    submit = SubmitField("Set new password")

class EmailOTPForm(FlaskForm):
    email_otp = StringField("Email Verification Code", validators=[DataRequired(), Length(min=6, max=6, message="Please enter the 6-digit code")])
    submit = SubmitField("Verify Email")



class ResendOTPForm(FlaskForm):
    submit = SubmitField("Resend Code") 
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("Le mot de passe doit contenir au moins 8 caractères."),
                code='password_too_short',
            )
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une lettre majuscule."),
                code='password_no_upper',
            )
        
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une lettre minuscule."),
                code='password_no_lower',
            )
        
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un chiffre."),
                code='password_no_digit',
            )
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*()_+-=[]{}|;:,.<>?)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Votre mot de passe doit contenir au moins 8 caractères, "
            "incluant des lettres majuscules, minuscules, des chiffres et des caractères spéciaux."
        )

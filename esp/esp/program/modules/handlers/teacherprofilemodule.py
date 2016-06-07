__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 by the individual contributors
  (see AUTHORS file)

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

Contact information:
MIT Educational Studies Program
  84 Massachusetts Ave W20-467, Cambridge, MA 02139
  Phone: 617-253-4882
  Email: esp-webmasters@mit.edu
Learning Unlimited, Inc.
  527 Franklin St, Cambridge, MA 02139
  Phone: 617-379-0178
  Email: web-team@learningu.org
"""
from esp.program.modules.base import ProgramModuleObj, needs_teacher, main_call, meets_deadline
from esp.program.models import RegistrationProfile
from esp.users.models import ESPUser
from django.db.models.query import Q
from esp.middleware.threadlocalrequest import get_current_request


class TeacherProfileModule(ProgramModuleObj):
    @classmethod
    def module_properties(cls):
        return {
            "admin_title": "Teacher Profile Editor",
            "link_title": "Update Your Profile",
            "module_type": "teach",
            "seq": 1,
            "required": True
        }

    def teachers(self, QObject=False):
        # TODO(benkraft): share code with the students version.
        if QObject:
            return {'teacher_profile': Q(registrationprofile__program=self.program) &
                                       Q(registrationprofile__teacher_info__isnull=False)}
        teachers = ESPUser.objects.filter(registrationprofile__program = self.program, registrationprofile__teacher_info__isnull = False).distinct()
        return {'teacher_profile': teachers}

    def teacherDesc(self):
        return {'teacher_profile': """Teachers who have filled out a profile"""}

    @main_call
    @needs_teacher
    @meets_deadline("/Profile")
    def profile(self, request, tl, one, two, module, extra, prog):
        """ Display the registration profile page, the page that contains the contact information for a teacher, as attached to a particular program """
        from esp.web.views.myesp import profile_editor
        response = profile_editor(request, prog, False, 'teacher')
        if response == True:
            return self.goToCore(tl)
        return response

    def isCompleted(self):
        regProf = RegistrationProfile.getLastForProgram(get_current_request().user, self.program)
        return regProf.id is not None

    class Meta:
        proxy = True
        app_label = 'modules'
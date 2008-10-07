
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: web@esp.mit.edu
"""
from django.core.files.base import ContentFile

from esp.users.models     import ESPUser
from esp.program.models   import TeacherBio, Program, ArchiveClass
from esp.web.util         import get_from_id, render_to_response
from esp.datatree.models  import GetNode
from django               import forms
from django.http          import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from esp.middleware       import ESPError


@login_required
def bio_edit(request, tl='', last='', first='', usernum=0, progid = None, external = False, username=''):
    """ Edits a teacher bio """
    from esp.web.forms.bioedit_form import BioEditForm
    
    if tl == '':
        founduser = ESPUser(request.user)
    else:
	if username != '':
            founduser = ESPUser.objects.get(username=username)
        else:
            founduser = ESPUser.getUserFromNum(first, last, usernum)

    if not founduser.isTeacher():
        raise ESPError(False), '%s is not a teacher of ESP.' % \
                               (founduser.name())

    if request.user.id != founduser.id and request.user.is_staff != True:
        raise ESPError(False), 'You are not authorized to edit this biography.'
        
    
    foundprogram = get_from_id(progid, Program, 'program', False)

    lastbio      = TeacherBio.getLastBio(founduser)
        
    
    # if we submitted a newly edited bio...
    if request.method == 'POST' and request.POST.has_key('bio_submitted'):
        form = BioEditForm(request.POST, request.FILES)

        if form.is_valid():
            if foundprogram is not None:
                # get the last bio for this program.
                progbio = TeacherBio.getLastForProgram(founduser, foundprogram)
            else:
                progbio = lastbio

            # the slug bio and bio
            progbio.slugbio  = form.cleaned_data['slugbio']
            progbio.bio      = form.cleaned_data['bio']
            
            progbio.save()
            # save the image
            if form.cleaned_data['picture'] is not None:
                try:
                    picture = form.cleaned_data['picture']
                    picture.seek(0)
                    progbio.picture.save(picture.name, ContentFile(picture.read()))
                except:
                    #   If you run into a problem processing the image, just ignore it.
                    progbio.picture = lastbio.picture
                    progbio.save()
            else:
                progbio.picture = lastbio.picture
                progbio.save()
            if external:
                return True
            return HttpResponseRedirect(progbio.url())
        
    else:
        formdata = {'slugbio': lastbio.slugbio, 'bio': lastbio.bio, 'picture': lastbio.picture}
        form = BioEditForm(formdata)
        
    return render_to_response('users/teacherbioedit.html', request, GetNode('Q/Web/myesp'), {'form':    form,
                                                   'user':    founduser,
                                                   'picture_file': lastbio.picture})

    
    

def bio(request, tl, last = '', first = '', usernum = 0, username = ''):
    """ Displays a teacher bio """

    if username != '':
	founduser = ESPUser.objects.get(username=username)
    else:
        founduser = ESPUser.getUserFromNum(first, last, usernum)

    if not founduser.isTeacher():
        raise ESPError(False), '%s is not a teacher of ESP.' % \
                               (founduser.name())
    
    bio = TeacherBio.getLastBio(founduser)
    if bio.picture is None:
        bio.picture = 'not-available.jpg'
        
    if bio.slugbio is None or len(bio.slugbio.strip()) == 0:
        bio.slugbio = 'ESP Teacher'
    if bio.bio is None or len(bio.bio.strip()) == 0:
        bio.bio     = 'Not Available.'


    classes = ArchiveClass.getForUser(founduser)

    return render_to_response('users/teacherbio.html', request, GetNode('Q/Web/Bio'), {'biouser': founduser,
                                               'bio': bio,
                                               'classes': classes})


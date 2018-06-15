from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.forms import formset_factory
from django.conf import settings

from .forms import PostForm, UploadFileForm
from .models import Post
from . import object_detection
from .change_background import changeBackground


STATIC_DIR = settings.STATIC_ROOT + '/'
background_path = STATIC_DIR + "img/background/background.jpg"

cfg_filename = 'default_cfg'
weights_filename = 'default_weights'
names_filename = 'default_names'
background_filename = 'default_backgroud'

cfg_path = STATIC_DIR + "net/cfg.cfg"
weights_path = STATIC_DIR + "net/weights.weights"
meta_path = STATIC_DIR + "/net/data.data"
names_path = STATIC_DIR + "/net/names.names"

output_path = settings.STATICFILES_DIRS[0] + "/img/a.jpg"
net = object_detection.load_net(cfg_path, weights_path)
import os
print(os.getcwd())
meta = object_detection.load_meta(meta_path)



def handle_uploaded_file(f, outputFilename):
    destination = open(outputFilename, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def set_post_detail_context(instance, \
                            cfg_filename, \
                            weights_filename, \
                            names_filename, \
                            background_filename):
    return dict({
        "title": instance.title,
        "instance": instance,
        "cfg_filename": cfg_filename,
        "weights_filename": weights_filename,
        "names_filename": names_filename,
        "background_filename": background_filename
    })


def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        context = set_post_detail_context(instance, \
                                    cfg_filename, \
                                    weights_filename, \
                                    names_filename, \
                                    background_filename)
        return HttpResponseRedirect(instance.get_absolute_url())
    
    context = {
        "form": form,
    }
    return render(request, "post_form.html", context)



def post_detail(request, id=None):
    global background_path, cfg_filename, weights_filename
    global names_filename, background_filename
    global net, meta
    instance = get_object_or_404(Post, id=id)
    
    if request.GET.get("object_detection"):
        object_detection.detect(net, meta, instance.image.path, output_path)
        return render(request, "get_result.html")
    
    elif request.GET.get("change_background"):
         changeBackground(instance.image.path, background_path, net, meta, output_path)
         return render(request, "get_result.html")

    elif request.GET.get("save_result"):
        save_result(output_path)
    
    elif request.POST.get('choose_background'):
        form = UploadFileForm(request.POST, request.FILES)
        handle_uploaded_file(request.FILES['background_file'], background_path)
        background_filename = request.FILES['background_file'].name

    elif request.POST.get('choose_cfg'):
        form = UploadFileForm(request.POST, request.FILES)
        handle_uploaded_file(request.FILES['cfg_file'], cfg_path)
        del net
        net = object_detection.load_net(cfg_path, weights_path)
        cfg_filename = request.FILES['cfg_file'].name

    elif request.POST.get('choose_weights'):
        form = UploadFileForm(request.POST, request.FILES)
        handle_uploaded_file(request.FILES['weights_file'], weights_path)
        del net
        net = object_detection.load_net(cfg_path, weights_path)
        weights_filename = request.FILES['weights_file'].name

    elif request.POST.get('choose_names'):
        form = UploadFileForm(request.POST, request.FILES)
        handle_uploaded_file(request.FILES['names_file'], names_path)
        del meta
        meta = object_detection.load_meta(meta_path)
        names_filename = request.FILES['names_file'].name
    
    context = set_post_detail_context(instance, \
                                    cfg_filename, \
                                    weights_filename, \
                                    names_filename, \
                                    background_filename)
    return render(request, "post_detail.html", context)



def post_list(request):
    queryset_list = Post.objects.all() #.order_by("-timestamp")
    paginator = Paginator(queryset_list, 10) # Show 25 contacts per page
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)


    context = {
        "object_list": queryset, 
        "title": "List",
        "page_request_var": page_request_var
    }
    return render(request, "post_list.html", context)



def post_update(request, id=None):
    instance = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        "title": instance.title,
        "instance": instance,
        "form":form,
    }
    return render(request, "post_form.html", context)



def post_delete(request, id=None):
    instance = get_object_or_404(Post, id=id)
    instance.delete()
    messages.success(request, "Successfully deleted")
    return redirect("posts:list")



def save_result(path):
        data = fp.read()
        #filename = '/home/lamductan/FIT/MachineLearning/output.jpg'
        filename = "lamductan_love_tangyphung.jpg"
        response = HttpResponse(data, content_type="img/jpg")
        response['Content-Disposition'] = 'attachment'
        response.write(data)
        print(filename)
        return response
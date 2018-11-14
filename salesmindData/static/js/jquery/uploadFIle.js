/**
 * Created by Tiany on 2014/12/12 0012.
 */
/**
 * 使用ajaxupload上传文件<br>
 * 只引入这个js和jquery就可以
 */
/**
 * ajaxupload的封装，在ajaxupload的基础上添加了文件后缀验证。
 * @param opts - name : 上传文件的表单名称，对象后台接收对象，默认为file
 * action : 文件上传请求地址
 * fileType : 上传的文件类型，pic - 图片,video - 视频，attach - 附件
 * fileNum : 一次能同时上传的文件数量，默认1
 * onSubmit : 请求提交前的回调方法，return false 则不提交，参数文件和后缀（如：zip,jpg,gif）
 * onComplete : 请求完成的回调方法，参数文件和响应
 */
$.fn.extend({
    ajaxUpload : function(opts){
        var interval = null;
        var _this = this;
        var _thisOrginalText = null;
        var options = {
            fileType : opts.fileType || "pic",
            fileNum : (opts.fileNum && !isNaN(opts.fileNum)) ? opts.fileNum : 1,
            submit : opts.onSubmit,
            complete : opts.onComplete ,
            name : opts.name || "file",
            action : opts.action || ""
        };

        var ajaxUplaod = new AjaxUpload(_this,{
            action : options.action,
            name :  options.name,
            onSubmit : function(file, ext){
                if(typeof (options.submit) == "function"){
                   return options.submit(file, ext);
                }
            },
            onComplete : function(file, response){
                _this.text(_thisOrginalText);
                clearInterval(interval);
                _this.removeAttr("disabled");
                if(typeof (options.complete) == "function"){

                    response = response || "";
                    response = response.replace(/^.*(\{.*\}).*$/g, function (a, b) {
                        return b;
                    });

                    try{
                        response = $.parseJSON(response);
                    }catch (e){
                        try {
                            response = eval("("+response+")");
                        }catch(e1) {}
                    }
                    options.complete(file, response);
                }
            }
        });


        var showLoading = function (){
            _thisOrginalText = _this.text();
            _this.text('文件上传中');

            if( options.fileNum == 1)
                _this.attr("disabled","disabled");

            interval = window.setInterval(function(){
                var text = _this.text();
                if (text.length < 14){
                    _this.text(text + '.');
                } else {
                    _this.text('文件上传中');
                }
            }, 200);
        };
    }
});
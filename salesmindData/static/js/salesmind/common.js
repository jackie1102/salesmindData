var wait = 60;
/**
 * ajax post提交
 * @param url
 * @param params
 * @returns {*}
 */
function post(url,params){
    var returnData;
    $.ajax({
        type:"POST",
        dataType:"json",
        data:params,
        url:url,
        async:false,
        success:function(data){
            returnData = data;
        },
        error:function(e){
            returnData = e;
        }
    });
    return returnData;
}
/**
 * 获取浏览器地址参数
 * @param name
 * @returns {*}
 */
function getQueryString(name) {
    var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var r = window.location.search.substr(1).match(reg);
    if (r != null) return decodeURI(r[2]); return null;
}

//退出登录
$("#aLogout").bind("click", function() {
    layer.confirm("<div style='padding: 0px 20px;'>确定退出吗？</div>", {
        icon : 7
        ,btn : [ '确定', '取消' ]
        ,btnAlign: 'c'
    }, function(index) {
        window.location = "/sysuser/logout/";
    }, function(index) {
        layer.close(index);
    });
});

function upload(task_id,param) {
    layui.use(['element','layer','upload'],function() {
        var element = layui.element, layer = layui.layer, upload = layui.upload;
        var uploadInst = upload.render({
                elem: "#upload" + task_id //绑定元素
                ,url: '/spider/start_task1/'//上传接口
                ,accept:"file"
                ,exts:'xls|xlsx'
                ,size: 0
                ,before:function () {
                    this.data = param
                }
                ,done: function(res){
                    if(res.errId == '0'){
                        layer.open({
                            title: ['提示', 'padding-left:80px;text-align: center;'],
                            content: "<p style='text-align: center'>上传成功</p>",
                            offset: '100px',
                            btn: ['确定'],
                            btnAlign: 'c',
                            yes: function (index) {
                                layer.close(index);
                                var state1 = document.getElementById(task_id +'_1');
                                state1.innerText='已完成';
                            }
                        });
                    }else{
                        layer.msg(res.errMsg,{icon: 2,offset: '100px'});
                    }
                }
                ,error: function(){}
            });
        });
    }
function layuiLoading(){
        layui.use(['layer', 'form'], function(){
                index = layer.load(0, {shade: false});
        });
}
function layuiRemoveLoading(){
        layui.use(['layer', 'form'], function(){
                var layer = layui.layer
                layer.close(index);
                });
}

/**
 * 打开所在行业
 * */
function open_job51_industry(id) {
    layer.open({
        type:2,
        area: ['500px', '550px'],
        content: '/spider/open_job51_industry/?id='+id
    });
}
/**
 * 打开地区
 * */
function open_job51_area(id) {
    layer.open({
        type:2,
        area: ['910px', '490px'],
        content: '/spider/open_job51_area/?id='+id
    });
}
/**
 * 打开职能
 */
function open_job51_jobs(id){
    layer.open({
        type:2,
        area: ['1100px', '490px'],
        content: '/spider/open_job51_jobs/?id='+id
    });
}
/**
 * 打开期望工作地
 * */
function open_job51_exp_area(id) {
    layer.open({
        type:2,
        area: ['1100px', '490px'],
        content: '/spider/open_job51_exp_area/?id='+id
    });
}
/**
 * 打开专业
 * */
function open_job51_major(id) {
    layer.open({
        type:2,
        area: ['800px', '490px'],
        content: '/spider/open_job51_major/?id='+id
    });
}
/**
 * 打开户口所在地
 * */
function open_job51_residence(id){
    layer.open({
        type:2,
        area: ['1100px', '490px'],
        content: '/spider/open_job51_residence/?id='+id
    });
}
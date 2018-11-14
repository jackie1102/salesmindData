/**
 * 打开户口所在地
 */
function open_residence(id) {
    layer.open({
        type:2,
        area: ['950px', '450px'],
        content: '/spider/open_residence/?id='+id
    });
}
/**
 *打开语言能力
 */
function open_languages(id) {
    layer.open({
        type:2,
        area: ['340px', '280px'],
        content: '/spider/open_languages/?id='+id
    });
}
/**
 *打开期望从事行业
 */
function open_exp_industry(id) {
    layer.open({
        type:2,
        area: ['550px', '550px'],
        content: '/spider/open_exp_industry/?id='+id
    });
}
/**
 *打开期望工作地区
 */
function open_exp_area(id) {
    layer.open({
        type:2,
        area: ['950px', '450px'],
        content: '/spider/open_exp_area/?id='+id
    });
}
/**
 * 打开专业技能
 * */
function open_skills(id) {
    layer.open({
        type:2,
        area: ['400px', '330px'],
        content: '/spider/open_skills/?id='+id
    });
}
/**
 * 打开所在行业
 * */
function open_industry(id) {
    layer.open({
        type:2,
        area: ['550px', '550px'],
        content: '/spider/open_industry/?id='+id
    });
}
/**
 * 打开期望从事职业
 * */
function open_exp_position(id) {
    layer.open({
        type:2,
        area: ['910px', '450px'],
        content: '/spider/open_exp_position/?id='+id
    });
}
/**
 * 打开职业类别
 * */
function open_position(id) {
    layer.open({
        type:2,
        area: ['1200px', '500px'],
        content: '/spider/open_position/?id='+id
    });
}
/**
 * 打开现居住地
 * */
function open_area(id) {
    layer.open({
        type:2,
        area: ['910px', '450px'],
        content: '/spider/open_area/?id='+id
    });
}
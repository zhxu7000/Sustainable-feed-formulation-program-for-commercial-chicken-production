import requests from "./requests";

export const reqLogin = (data) => {
    return requests({
        url: "/api/login/",
        method: "post",
        data,
    });
};

export const reqRegister = (data) => {
    return requests({
        url: "/api/register/",
        method: "post",
        data,
    });
};

export const reqUser = (data) => {
    return requests({
        url: "/api/user_manage/",
        method: "post",
        data,
    });
};

//recipe crud
export const reqRecipeCRUD = (data) => {
    return requests({
        url: "/api/recipe_crud/",
        method: "post",
        data,
    });
};

export const reqBestRecipeCRUD = (data) => {
    return requests({
        url: "/api/best_recipe_crud/",
        method: "post",
        data,
    });
};

export const reqAttributeCRUD = (data) => {
    return requests({
        url: "/api/recipe_attribute_limit_crud/",
        method: "post",
        data,
    });
};
export const reqRecipeMaterialCRUD = (data) => {
    return requests({
        url: "/api/recipe_raw_material_crud/",
        method: "post",
        data,
    });
};
export const reqMaterialAttributeCRUD = (data) => {
    return requests({
        url: "/api/material_attribute_value_crud/",
        method: "post",
        data,
    });
};

export const reqRecipeRatioCRUD = (data) => {
    return requests({
        url: "/api/recipe_ratio_crud/",
        method: "post",
        data,
    });
};

export const reqCalculate = (data) => {
    return requests({
        url: "/api/calculate/",
        method: "post",
        data,
    });
};

export const reqSetTonne = (data) => {
    return requests({
        url: "/api/set_tonne/",
        method: "post",
        data,
    });
};

export const reqImportExcel = (data) => {
    return requests({
        url: "/api/import_excel/",
        method: "post",
        data: data,
        headers: {
            "Content-Type": "multipart/form-data",
        },
        withCredentials: true,
    });
};

export const reqExportExcel = () => {
    return requests({
        url: "/api/export_excel/",
        method: "get",
        responseType: "blob", // Important to set this for binary data
    });
};

export const reqDownloadPDF = (data) => {
    return requests({
        url: "/api/download_pdf/",
        method: "post",
        data,
    });
};

export const getMaterialCostWeightPercentage = async (data) => {
    const { recipeId } = data;
    try {
        const response = await fetch(`/api/get_material_cost/?recipe_id=${recipeId}`);
        const responseData = await response.json();
        if (responseData.status === "success") {
            return responseData.data;
        } else {
            console.error("Error from server:", responseData.message);
            return null;
        }
    } catch (error) {
        console.error("Error fetching data:", error);
        return null;
    }
};

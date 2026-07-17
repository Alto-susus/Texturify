# Texturify

<img width="1393" height="901" alt="image" src="https://github.com/user-attachments/assets/047697f8-604b-443f-a176-38e8586737ab" />


A native C++ desktop app for applying surface displacement textures to 3D meshes (STL / OBJ / 3MF
in, textured STL / 3MF out). Texturify is inspired by **[BumpMesh](https://bumpmesh.com)**
([CNCKitchen/stlTexturizer](https://github.com/CNCKitchen/stlTexturizer)) by Stefan Hermann / CNC
Kitchen — this is an independent native rewrite.

The mesh-processing pipeline (adaptive subdivision → regularization → displacement → QEM decimation → repair), the 24 built-in texturesare ported from the original web application.
___
Десктопное приложение на C++ для применения текстур со смещением поверхности к 3D-моделям (STL / OBJ / 3MF
на входе, текстурированный STL / 3MF на выходе). Texturify создан по мотивам **[BumpMesh](https://bumpmesh.com)**
([CNCKitchen/stlTexturizer](https://github.com/CNCKitchen/stlTexturizer)) автор: Стефан Херманн / CNC
Kitchen — это независимая авторская версия.

Пайплайн обработки сетки (адаптивное разделение → регуляризация → смещение → прореживание QEM → восстановление), 24 встроенных текстуры перенесены из исходного веб-приложения.

## Download/Скачать

You can download latest version via [Releases](https://github.com/Alto-susus/texturify/releases) page.
___

Скачать последнюю версию можно на вкладке [Релизы](https://github.com/Alto-susus/texturify/releases).
## Building/Сборка (Windows)

Requires Visual Studio 2022 and CMake ≥ 3.20.
___
Требуется Visual Studio 2022 и CMake ≥ 3.20.

```bash
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
build/Release/texturify.exe
```

## Third-party

- [Dear ImGui](https://github.com/ocornut/imgui) (MIT), [GLFW](https://glfw.org) (zlib), [stb](https://github.com/nothings/stb) (public domain/MIT), [miniz](https://github.com/richgel999/miniz) (MIT)
- Fonts: Instrument Sans, Noto Sans / JP / KR (OFL), JetBrains Mono (OFL)
- Texture images and translations from the original project (AGPL-3.0)

## License

GNU GPL v3.0 — see [LICENSE](LICENSE).

Original work © CNCKitchen (Stefan Hermann). Texturify is derivative work under GPL license.

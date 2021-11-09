
// Example Pixel Shader
// uniform int NumMasks;

// sampler defines
#define COORDS sTD2DInputs[0]
#define MISC sTD2DInputs[1]

#define MASKS sTD2DArrayInputs[0]
#define PIXFRAMES sTD2DArrayInputs[1]
#define COORDSETS sTD2DArrayInputs[2]

#define ProjTex0 sTD2DInputs[2]
#define ProjTex1 sTD2DInputs[3]
#define ProjTex2 sTD2DInputs[4]
#define ProjTex3 sTD2DInputs[5]
#define ProjTex4 sTD2DInputs[6]
#define ProjTex5 sTD2DInputs[7]
#define ProjTex6 sTD2DInputs[8]
#define ProjTex7 sTD2DInputs[9]
#define ProjTex8 sTD2DInputs[10]
#define ProjTex9 sTD2DInputs[11]
#define ProjTex10 sTD2DInputs[12]
#define ProjTex11 sTD2DInputs[13]
#define ProjTex12 sTD2DInputs[14]
#define ProjTex13 sTD2DInputs[15]
#define ProjTex14 sTD2DInputs[16]
#define ProjTex15 sTD2DInputs[17]

// uniforms
uniform samplerBuffer Misc;
uniform samplerBuffer Proj_Params;
uniform samplerBuffer realtimeData;
uniform samplerBuffer PixframeControl;

uniform int ProjectorBufferSize;
uniform ivec3 ViewportChanIndicies;
uniform int NumPasses;
uniform float selectionPulse;
uniform int maskPreviewIndex;
uniform int NumPixFrameContribs;


#include <GLSL_SamplerFunctions>



out vec4 fragColor;
void main()
{
	
	ivec2 	RES 			= ivec2(uTDOutputInfo.res.zw);
	ivec2 	PixelCoords2D 	= ivec2(vUV.st * RES);
	int 	PixelCoords1D 	= PixelCoords2D.x + (PixelCoords2D.y * RES.x);
	
	// we get the world space coordinates of the Pix. We might eventually want to get other coordinate sets
	vec4 	Coords_WS 		= vec4( texelFetch(COORDS, PixelCoords2D , 0).xyz , 1 ); // currently not used! guess we can leave it in for now though.
	float 	CoordsIndex 	= texelFetch(COORDS, PixelCoords2D , 0).w;
	vec4 	Coords_MISC 	= texelFetch(MISC, PixelCoords2D , 0).rgba;

	// float DEBUG_VAR = 0;

	// assemble and sample the 4 coordinate sets into an array. based on what the projector needs, we will pull from the apropriate one.
	vec4 CoordinateSets[4];
	CoordinateSets[0] = texelFetch(COORDSETS, ivec3(PixelCoords2D,0) , 0).xyzw;
	CoordinateSets[1] = texelFetch(COORDSETS, ivec3(PixelCoords2D,1) , 0).xyzw;
	CoordinateSets[2] = texelFetch(COORDSETS, ivec3(PixelCoords2D,2) , 0).xyzw;
	CoordinateSets[3] = texelFetch(COORDSETS, ivec3(PixelCoords2D,3) , 0).xyzw;

	// get some fixture parameters.
	int 	UtilizationMask = int(Coords_MISC.x);
	int 	currentChanIndex= int(Coords_MISC.y);
	bool 	Selected 		= bool(Coords_MISC.z);
	bool 	FixtureActive 	= bool(Coords_MISC.w);

	// float 	PixScale 		= Coords_MISC2.x;

	vec4 	finalColor 		= vec4(0,0,0,1);
	vec4 	color 			= vec4(0.0);

	// get number of pixframes by dividing the length of the control buffer by the number of attributes each frame is represented by.
	int NumberOfControls 	= 3; // 3 controls per contribution. [pixframeIndex, pixframeIntensity, pixframeBlendMode]

	ProjectorObject pObj;
	
	for( int i=0; i<NumPasses; i++ )
	{

	 	// i = 4;

	 	
	 	vec4	realtimeDataFetch 	= texelFetch(realtimeData, i);
		float 	FadeScale 			= realtimeDataFetch.x;
		int 	TextureIndex 		= int(realtimeDataFetch.y);
		int 	projectorIndex 		= int(realtimeDataFetch.z);
		bool 	constantColor 		= bool(realtimeDataFetch.w);

		if( FadeScale > 0 ){

		
		 	// get the projector object by index.
			pObj = GetProjector(projectorIndex);

			if( pObj.Projectoractive == true ){

			 	// convert the world space Pix coordinates into projector space 0:1
				vec4 ProjectorSpaceCoordinates = WorldSpace_to_ProjectorSpace( CoordinateSets[ pObj.Coordinateset ] , CoordsIndex , pObj );

			 	// handles the wrapping, or mirroring of uvs in glsl, so we can control this per projector.
				ProjectorSpaceCoordinates = Apply_Extend_Modes( ProjectorSpaceCoordinates , pObj );

			 	// this function returns a mask, 0 or 1, that represents where the projector is hitting, where it isnt(behind), etc.
				float ProjectorCullMask = Cull_Pix_Against_Projector( ProjectorSpaceCoordinates , pObj , UtilizationMask );

				// generates the projector mask. Will be 1 if the fixture has no masks, otherwise will try to bool equate as a mask.
				float projectorMaskV2 = Generate_Projector_Masks_V2( PixelCoords2D , pObj , currentChanIndex );

				vec4 ProjectorSampledTexture = vec4(0);
				vec4 constColor = vec4(0);
				if( constantColor == true ){

				 	// this function contributes the constant color, previously known as color override to the appropriate channels.
					constColor = Contribute_ConstantColor_To_Buffer( pObj , currentChanIndex , ProjectorCullMask );

				}

				else{

				 	// sample the correct projector texture based on index, and then apply the mask.
					ProjectorSampledTexture = Sample_Projector_Texture( ProjectorSpaceCoordinates , ProjectorCullMask , TextureIndex );

				}

			 	// this function contributes the sampled texture, to the buffer, while masking it to only the pixels who contain that channel index.
				float newVal = Contribute_Texture_To_Buffer( color , ProjectorSampledTexture , pObj , currentChanIndex , constColor , projectorMaskV2 );
				color.r = mix( color.r , newVal , FadeScale );

			}

		// break;
		}

	}

	// applies the pixframes to their respective routing channels.
	color.r = Apply_PixFrames( color , PixelCoords2D , NumPixFrameContribs , NumberOfControls );
	
	// write out color to final color.
	finalColor.r += color.r;

	// this function causes us to temporarily switch into a preview mode for visualizing our masks. when a user hovers a mask in the mask editor, it highlights in viewport.
	finalColor.r = Contribute_MaskHighlight_To_Buffer( finalColor, PixelCoords2D , currentChanIndex );

	// this function modifies the color buffer, to overwrite pure green where the fixture is selected, or the fixture's Pix is selected while in Pix mode.
	finalColor.r = Contribute_SelectionHighlight_To_Buffer( finalColor, Selected , currentChanIndex );

	// clamp 
	finalColor.r = min( finalColor.r , 1.0 );
	finalColor.r = max( finalColor.r , 0.0 );
	

	//////////////////////////// DEBUG //////////////////////////////////
	// finalColor.r = 0;
	// finalColor.r = DEBUG_VAR;
	// finalColor.r = NumPasses;

	// ProjectorObject pObj = GetProjector(1);

	// if(PixelCoords1D == 0) { finalColor.r = float(pObj.Pscale) ;}
	// if(PixelCoords1D == 1) { finalColor.r = float(pObj.Pstyle) ;}
	// if(PixelCoords1D == 2) { finalColor.r = float(pObj.Pextend) ;}

	// if(PixelCoords1D == 3) { finalColor.r = float(pObj.Routingr) ;}
	// if(PixelCoords1D == 4) { finalColor.r = float(pObj.Routingg) ;}
	// if(PixelCoords1D == 5) { finalColor.r = float(pObj.Routingb) ;}
	// if(PixelCoords1D == 6) { finalColor.r = float(pObj.Routinga) ;}

	// if(PixelCoords1D == 7) { finalColor.r = float(pObj.Maskmode) ;}

	// if(PixelCoords1D == 8) { finalColor.r = float(pObj.Setcolorr) ;}
	// if(PixelCoords1D == 9) { finalColor.r = float(pObj.Setcolorg) ;}
	// if(PixelCoords1D == 10) { finalColor.r = float(pObj.Setcolorb) ;}
	// if(PixelCoords1D == 11) { finalColor.r = float(pObj.Setcolora) ;}

	// if(PixelCoords1D == 12) { finalColor.r = float(pObj.Projectoractive) ;}

	// if(PixelCoords1D == 13) { finalColor.r = float(pObj.Gamma) ;}
	// if(PixelCoords1D == 14) { finalColor.r = float(pObj.Gain) ;}

	// if(PixelCoords1D == 15) { finalColor.r = float(pObj.Projectorblendmode) ;}
	// if(PixelCoords1D == 16) { finalColor.r = float(pObj.Projectorlayer) ;}



	fragColor = TDOutputSwizzle(finalColor);
}
